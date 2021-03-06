# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)

SUBCONTRACT_REQUISITION_STATES = [
    ('draft', 'Draft'),
    ('ongoing', 'Ongoing'),
    ('in_progress', 'Confirmed'),
    ('open', 'Bid Selection'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled')
]


class SubcontractRequisitionType(models.Model):
    _name = "subcontract.requisition.type"
    _description = "Subcontract Requisition Type"
    _order = "sequence"

    name = fields.Char(string='Agreement Type', required=True, translate=True)
    sequence = fields.Integer(default=1)
    exclusive = fields.Selection([
        ('exclusive', 'Select only one RFQ (exclusive)'), ('multiple', 'Select multiple RFQ')],
        string='Agreement Selection Type', required=True, default='multiple',
        help="""Select only one RFQ (exclusive):  when a subcontract order is confirmed, cancel the remaining subcontract order.\n
                    Select multiple RFQ: allows multiple subcontract orders. On confirmation of a subcontract order it does not cancel the remaining orders""")
    quantity_copy = fields.Selection([
        ('copy', 'Use quantities of agreement'), ('none', 'Set quantities manually')],
        string='Quantities', required=True, default='none')
    line_copy = fields.Selection([
        ('copy', 'Use lines of agreement'), ('none', 'Do not create RfQ lines automatically')],
        string='Lines', required=True, default='copy')


class SubcontractRequisition(models.Model):
    _name = 'subcontract.requisition'
    _inherit = ['mail.thread']
    _order = "id desc"

    def _get_picking_in(self):
        pick_in = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
        company = self.env['res.company']._company_default_get('subcontract.requisition')
        if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
            pick_in = self.env['stock.picking.type'].search(
                [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                limit=1,
            )
        return pick_in

    def _get_type_id(self):
        return self.env['subcontract.requisition.type'].search([], limit=1)

    name = fields.Char(string='Agreement Reference', required=True, copy=False, default='New')
    origin = fields.Char(string='Source Document')
    order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')
    vendor_id = fields.Many2one('res.partner', string="Subcontractor", domain=[('subcontractor', '=', True)])
    type_id = fields.Many2one('subcontract.requisition.type', string="Agreement Type", required=True,
                              default=_get_type_id)
    ordering_date = fields.Date(string="Ordering Date", track_visibility='onchange')
    date_end = fields.Datetime(string='Agreement Deadline', track_visibility='onchange')
    schedule_date = fields.Date(string='Delivery Date', index=True,
                                help="The expected and scheduled delivery date where all the products are received",
                                track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Subcontract Representative', default=lambda self: self.env.user)
    description = fields.Text()
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'subcontract.requisition'))
    subcontract_ids = fields.One2many('subcontract.order', 'requisition_id', string='Subcontract Orders',
                                      states={'done': [('readonly', True)]})
    invoice_ids = fields.One2many('account.invoice', 'subcontract_requisition_id', string='Invoices',
                                  states={'done': [('readonly', True)]})
    line_ids = fields.One2many('subcontract.requisition.line', 'requisition_id', string='Order Lines',
                               states={'done': [('readonly', True)]}, copy=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    state = fields.Selection(SUBCONTRACT_REQUISITION_STATES,
                             'Status', track_visibility='onchange', required=True,
                             copy=False, default='draft')
    state_blanket_order = fields.Selection(SUBCONTRACT_REQUISITION_STATES, compute='_set_state')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, default=_get_picking_in)
    is_quantity_copy = fields.Selection(related='type_id.quantity_copy', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    account_analytic_id = fields.Many2one('account.analytic.account', string="Project")
    category_id = fields.Many2one('subcontract.category', string="Category")
    stock_picking_id = fields.Many2one('stock.picking.type', domain=[('code', '=', 'incoming')], string="Delivery To")
    prev_amount = fields.Float()
    previ_qty = fields.Float()
    last_seq = fields.Integer(default=1)

    @api.depends('state')
    def _set_state(self):
        self.state_blanket_order = self.state

    @api.onchange('vendor_id')
    def _onchange_vendor(self):
        requisitions = self.env['subcontract.requisition'].search([
            ('vendor_id', '=', self.vendor_id.id),
            ('state', '=', 'ongoing'),
            ('type_id.quantity_copy', '=', 'none'),
        ])
        if any(requisitions):
            title = _("Warning for %s") % self.vendor_id.name
            message = _(
                "There is already an open blanket order for this supplier. We suggest you to use to complete this open blanket order instead of creating a new one.")
            warning = {
                'title': title,
                'message': message
            }
            return {'warning': warning}

    @api.multi
    @api.depends('subcontract_ids')
    def _compute_orders_number(self):
        for requisition in self:
            requisition.order_count = len(requisition.subcontract_ids)

    @api.multi
    def action_cancel(self):
        # try to set all associated quotations to cancel state
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
            requisition.subcontract_ids.button_cancel()
            for co in requisition.subcontract_ids:
                co.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
        self.write({'state': 'cancel'})

    @api.multi
    def action_in_progress(self):
        self.ensure_one()
        if not all(obj.line_ids for obj in self):
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.") % self.name)
        if self.type_id.quantity_copy == 'none' and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            self.write({'state': 'ongoing'})
        else:
            self.write({'state': 'in_progress'})
        # Set the sequence number regarding the requisition type
        if self.name == 'New':
            if self.is_quantity_copy != 'none':
                self.name = self.env['ir.sequence'].next_by_code('subcontract.requisition.subcontract.tender')
            else:
                self.name = self.env['ir.sequence'].next_by_code('subcontract.requisition.blanket.order')

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})

    def action_draft(self):
        self.ensure_one()
        self.name = 'New'
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        """
        Generate all subcontract order based on selected lines, should only be called on one agreement at a time
        """
        if any(subcontract_order.state in ['draft', 'sent', 'to approve'] for subcontract_order in
               self.mapped('subcontract_ids')):
            raise UserError(_('You have to cancel or validate every RfQ before closing the subcontract requisition.'))
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
        self.write({'state': 'done'})

    def _prepare_tender_values(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        return {
            'origin': origin,
            'date_end': values['date_planned'],
            'warehouse_id': values.get('warehouse_id') and values['warehouse_id'].id or False,
            'company_id': values['company_id'].id,
            'line_ids': [(0, 0, {
                'product_id': product_id.id,
                'product_uom_id': product_uom.id,
                'product_qty': product_qty,
                'move_dest_id': values.get('move_dest_ids') and values['move_dest_ids'][0].id or False,
            })],
        }

    def unlink(self):
        if any(requisition.state not in ('draft', 'cancel') for requisition in self):
            raise UserError(_('You can only delete draft requisitions.'))
        # Draft requisitions could have some requisition lines.
        self.mapped('line_ids').unlink()
        return super(SubcontractRequisition, self).unlink()


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"
    _order = 'sequence, subcontract_requisition_id desc, min_qty desc, price'

    subcontract_requisition_id = fields.Many2one('subcontract.requisition',
                                                 related='subcontract_requisition_line_id.requisition_id',
                                                 string='Blanket order', readonly=False)
    subcontract_requisition_line_id = fields.Many2one('subcontract.requisition.line')


class SubcontractRequisitionLine(models.Model):
    _name = "subcontract.requisition.line"
    _description = "Subcontract Requisition Line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Product Unit of Measure')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'))
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    price_ordered = fields.Float(compute='_compute_ordered_price', string='Ordered Price',
                                 digits=dp.get_precision('Product Price'))
    qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered Quantities',)
    price_invoiced = fields.Float(compute='_compute_invoiced_price', string='Invoiced Price',
                                  digits=dp.get_precision('Product Price'))
    qty_invoiced = fields.Float(compute='_compute_invoiced_qty', string='Invoiced Quantities')
    requisition_id = fields.Many2one('subcontract.requisition', required=True, string='Subcontract Agreement',
                                     ondelete='cascade')
    company_id = fields.Many2one('res.company', related='requisition_id.company_id', string='Company', store=True,
                                 readonly=True, default=lambda self: self.env['res.company']._company_default_get(
            'subcontract.requisition.line'))
    account_analytic_id = fields.Many2one('account.analytic.account', related='requisition_id.account_analytic_id',
                                          string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    schedule_date = fields.Datetime(string='Scheduled Date')
    move_dest_id = fields.Many2one('stock.move', 'Downstream Move')
    supplier_info_ids = fields.One2many('product.supplierinfo', 'subcontract_requisition_line_id')
    cost_code_id = fields.Many2one('subcontract.code', string="Cost Code")
    taxes_id = fields.Many2many('account.tax', string="Taxes", domain=[('type_tax_use', '=', 'purchase')])
    description = fields.Text(string="Description")
    previ_qty = fields.Float()
    previ_amount = fields.Float()
    my_total = fields.Float(string='Total', compute='CalcTotal')
    sequence = fields.Integer(string="Sequence", default=0, readonly=True)


    @api.multi
    @api.depends('price_unit','product_qty')
    def CalcTotal(self):
        for re in self:
            re.my_total = re.price_unit * re.product_qty

    @api.model
    def create(self, vals):
        res = super(SubcontractRequisitionLine, self).create(vals)
        if res.requisition_id.state not in ['draft', 'cancel',
                                            'done'] and res.requisition_id.is_quantity_copy == 'none':
            supplier_infos = self.env['product.supplierinfo'].search([
                ('product_id', '=', vals.get('product_id')),
                ('name', '=', res.requisition_id.vendor_id.id),
            ])
            if not [s.subcontract_requisition_id for s in supplier_infos]:
                res.create_supplier_info()
            if vals['price_unit'] <= 0.0:
                raise UserError(_('You cannot confirm the blanket order without price.'))
        res.sequence = res.requisition_id.last_seq
        res.requisition_id.last_seq +=1        
        return res

    @api.multi
    def write(self, vals):
        res = super(SubcontractRequisitionLine, self).write(vals)
        if 'price_unit' in vals:
            if vals['price_unit'] <= 0.0:
                raise UserError(_('You cannot confirm the blanket order without price.'))
            # If the price is updated, we have to update the related SupplierInfo
            self.supplier_info_ids.write({'price': vals['price_unit']})
        return res

    def unlink(self):
        to_unlink = self.filtered(lambda r: r.requisition_id.state not in ['draft', 'cancel', 'done'])
        to_unlink.mapped('supplier_info_ids').unlink()
        return super(SubcontractRequisitionLine, self).unlink()

    def create_supplier_info(self):
        subcontract_requisition = self.requisition_id
        if subcontract_requisition.type_id.quantity_copy == 'none' and subcontract_requisition.vendor_id:
            # create a supplier_info only in case of blanket order
            self.env['product.supplierinfo'].create({
                'name': subcontract_requisition.vendor_id.id,
                'product_id': self.product_id.id,
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'price': self.price_unit,
                'currency_id': self.requisition_id.currency_id.id,
                'subcontract_requisition_id': subcontract_requisition.id,
                'subcontract_requisition_line_id': self.id,
            })

    @api.multi
    @api.depends('requisition_id.subcontract_ids.state')
    def _compute_ordered_qty(self):
        for line in self:
            total = 0.0
            for sco in line.requisition_id.subcontract_ids.filtered(
                    lambda subcontract_order: subcontract_order.state in ['subcontract', 'done']):
                for sco_line in sco.order_line.filtered(lambda order_line: order_line.product_id == line.product_id and 
                    order_line.line_sequence == line.sequence):
                    if sco_line.product_uom != line.product_uom_id:
                        total += sco_line.product_uom._compute_quantity(sco_line.product_qty, line.product_uom_id)
                    else:
                        total += sco_line.product_qty
            line.qty_ordered = total

    @api.multi
    @api.depends('requisition_id.invoice_ids.state')
    def _compute_invoiced_qty(self):
        for line in self:
            total = 0.0
            for pg_inv in line.requisition_id.invoice_ids.filtered(lambda r: r.state not in ['draft', 'cancel']):
                for inv_line in pg_inv.invoice_line_ids.filtered(lambda r: r.product_id == line.product_id and 
                    r.line_sequence == line.sequence):
                    if inv_line.uom_id != line.product_uom_id:
                        total += inv_line.product_uom._compute_quantity(inv_line.quantity, line.product_uom_id)
                    else:
                        total += inv_line.quantity
            line.qty_invoiced = total

    @api.multi
    @api.depends('requisition_id.subcontract_ids.state')
    def _compute_ordered_price(self):
        for line in self:
            total = 0.0
            for sco in line.requisition_id.subcontract_ids.filtered(
                    lambda subcontract_order: subcontract_order.state in ['subcontract', 'done']):
                for sco_line in sco.order_line.filtered(lambda order_line: order_line.product_id == line.product_id and 
                    order_line.line_sequence == line.sequence):
                    if sco_line.order_id.currency_id != line.requisition_id.currency_id:
                        total += sco_line.order_id.currency_id.compute(sco_line.product_qty * sco_line.price_unit,
                                                                       line.requisition_id.currency_id)
                    else:
                        total += sco_line.product_qty * sco_line.price_unit
            line.price_ordered = total

    @api.multi
    @api.depends('requisition_id.invoice_ids.state')
    def _compute_invoiced_price(self):
        for line in self:
            total = 0.0
            for pg_inv in line.requisition_id.invoice_ids.filtered(lambda r: r.state not in ['draft', 'cancel']):
                for inv_line in pg_inv.invoice_line_ids.filtered(lambda r: r.product_id == line.product_id and 
                    r.line_sequence == line.sequence):
                    if inv_line.invoice_id.currency_id != line.requisition_id.currency_id:
                        total += inv_line.order_id.currency_id.compute(inv_line.quantity * inv_line.price_unit,
                                                                       line.requisition_id.currency_id)
                    else:
                        total += inv_line.quantity * inv_line.price_unit
            line.price_invoiced = total

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            self.product_qty = 1.0
        if not self.schedule_date:
            self.schedule_date = fields.Datetime.from_string(self.requisition_id.schedule_date)

    @api.multi
    def _prepare_subcontract_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        requisition = self.requisition_id
        date_planned = False
        if self.schedule_date:
            date_planned = datetime.combine(self.schedule_date, time.min)

        if not date_planned and requisition.schedule_date:
            date_planned = datetime.combine(requisition.schedule_date, time.min)
        elif not date_planned:
            date_planned = datetime.now()
        # print(self.taxes_id.ids,'Taxesss')
        _logger.error(taxes_ids)
        return {
            'name': self.description,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            # 'product_qty': product_qty,
            'product_qty': 0,
            'cost_code_id': self.cost_code_id.id,
            'price_unit': price_unit,
            # 'taxes_id': [243],#[(6, 0, taxes_ids)],#[(6,0,self.taxes_id.ids)],#mapped('id'))], #self.taxes_id.ids,#,
            'date_planned': date_planned,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'move_dest_ids': self.move_dest_id and [(4, self.move_dest_id.id)] or [],
            'previ_qty': self.previ_qty,
            'previ_amount': self.previ_amount,
            'line_sequence': self.sequence

        }


class SubcontractOrder(models.Model):
    _inherit = "subcontract.order"

    requisition_id = fields.Many2one('subcontract.requisition', string='Contract', copy=False)
    is_quantity_copy = fields.Selection(related='requisition_id.is_quantity_copy', readonly=False)


    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        self.account_analytic_id = requisition.account_analytic_id.id
        self.category = requisition.category_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.stock_picking_id.id

        if requisition.type_id.line_copy != 'copy':
            return

        # Create CO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context({
                'lang': partner.lang,
                'partner_id': partner.id,
            })
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.taxes_id.ids
            # taxes_ids = line.product_id.supplier_taxes_id.filtered(
            # lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Create PO line
            order_line_values = line._prepare_subcontract_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
            _logger.error(order_line_values)
        self.order_line = order_lines
    @api.multi
    def button_confirm(self):
        res = super(SubcontractOrder, self).button_confirm()
        for order in self:
            if order.requisition_id:
                for line in order.order_line:
                    requisition_line_ids = order.requisition_id.line_ids.filtered(
                        lambda r: r.product_id == line.product_id and r.sequence == line.line_sequence)
                    requisition_line_ids._compute_ordered_qty()
                    requisition_line_ids._compute_ordered_price()
                    for scr_line in requisition_line_ids:
                        if scr_line.product_qty < scr_line.qty_ordered:
                            scr_line.is_coloring = 't'
                            print('exceed', scr_line.is_coloring)
                            # raise Warning(
                            #     _("You shouldn't exceed the Contract quantity, please contact your administrator"))
                        if (scr_line.product_qty * scr_line.price_unit) < scr_line.price_ordered:
                            scr_line.is_coloring = 't'
                            print('exceed2',scr_line.is_coloring)
                            # raise Warning(_("You shouldn't exceed the Contract amount, please contact your administrator"))
        return res

    @api.multi
    def button_approve(self, force=False):
        res = super(SubcontractOrder, self).button_approve(force=force)
        for co in self:
            if not co.requisition_id:
                continue
            if co.requisition_id.type_id.exclusive == 'exclusive':
                others_co = co.requisition_id.mapped('subcontract_ids').filtered(lambda r: r.id != co.id)
                others_co.button_cancel()
                co.requisition_id.action_done()
        return res

    @api.model
    def create(self, vals):
        subcontract = super(SubcontractOrder, self).create(vals)
        if subcontract.requisition_id:
            subcontract.message_post_with_view('mail.message_origin_link',
                                               values={'self': subcontract, 'origin': subcontract.requisition_id},
                                               subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        return subcontract

    @api.multi
    def write(self, vals):
        result = super(SubcontractOrder, self).write(vals)
        if vals.get('requisition_id'):
            self.message_post_with_view('mail.message_origin_link',
                                        values={'self': self, 'origin': self.requisition_id, 'edit': True},
                                        subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        return result


class SubcontractOrderLine(models.Model):
    _inherit = "subcontract.order.line"

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(SubcontractOrderLine, self)._onchange_quantity()
        if self.order_id.requisition_id:
            for line in self.order_id.requisition_id.line_ids:
                if line.product_id == self.product_id and line.sequence == self.line_sequence:
                    if line.product_uom_id != self.product_uom:
                        self.price_unit = line.product_uom_id._compute_price(
                            line.price_unit, self.product_uom)
                    else:
                        self.price_unit = line.price_unit
                    break
        return res
    
    @api.model
    def create(self,vals):
        sub_order = self.env['subcontract.order'].browse(vals['order_id'])
        FiscalPosition = self.env['account.fiscal.position']
        fpos = False
        line = sub_order.requisition_id.line_ids.filtered(lambda x: x.sequence == vals['line_sequence'])
        if sub_order.partner_id:
            fpos = FiscalPosition.get_fiscal_position(sub_order.partner_id.id)
            fpos = FiscalPosition.browse(fpos)
        taxes_ids = []
        
        if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == subcontract.requisition.company_id)).ids
        else:
                taxes_ids = line.taxes_id.ids
        vals['taxes_id'] = [(6, 0, taxes_ids)]
        return super(SubcontractOrderLine, self).create(vals)



class ProductProduct(models.Model):
    _inherit = 'product.product'

    # def _prepare_sellers(self, params):
    #     if params and params.get('order_id'):
    #         return self.seller_ids.filtered(lambda s: not s.subcontract_requisition_id or s.subcontract_requisition_id == params['order_id'].requisition_id)
    #     else:
    #         return self.seller_ids


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subcontract_requisition = fields.Selection(
        [('rfq', 'Create a draft subcontract order'),
         ('tenders', 'Propose a call for tenders')],
        string='Procurement', default='rfq',
        help="Create a draft subcontract order: Based on your product configuration, the system will create a draft "
             "subcontract order.Propose a call for tender : If the 'subcontract_requisition' module is installed and this option "
             "is selected, the system will create a draft call for tender.")


class StockMove(models.Model):
    _inherit = "stock.move"

    requistion_line_ids = fields.One2many('subcontract.requisition.line', 'move_dest_id')


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_exceptions_domain(self):
        return super(ProcurementGroup, self)._get_exceptions_domain() + [('requistion_line_ids', '=', False)]


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if product_id.subcontract_requisition != 'tenders':
            return super(StockRule, self)._run_buy(product_id, product_qty, product_uom, location_id, name, origin,
                                                   values)
        values = self.env['subcontract.requisition']._prepare_tender_values(product_id, product_qty, product_uom,
                                                                            location_id, name, origin, values)
        values['picking_type_id'] = self.picking_type_id.id
        self.env['subcontract.requisition'].create(values)
        return True

    def _prepare_subcontract_order(self, product_id, product_qty, product_uom, origin, values, partner):
        res = super(StockRule, self)._prepare_subcontract_order(product_id, product_qty, product_uom, origin, values,
                                                                partner)
        res['partner_ref'] = values['supplier'].subcontract_requisition_id.name
        res['requisition_id'] = values['supplier'].subcontract_requisition_id.id
        if values['supplier'].subcontract_requisition_id.currency_id:
            res['currency_id'] = values['supplier'].subcontract_requisition_id.currency_id.id
        return res

    def _make_co_get_domain(self, values, partner):
        domain = super(StockRule, self)._make_co_get_domain(values, partner)
        if 'supplier' in values and values['supplier'].subcontract_requisition_id:
            domain += (
                ('requisition_id', '=', values['supplier'].subcontract_requisition_id.id),
            )
        return domain


class StockMove(models.Model):
    _inherit = 'stock.move'

    requisition_line_ids = fields.One2many('subcontract.requisition.line', 'move_dest_id')

    def _get_upstream_documents_and_responsibles(self, visited):
        if self.requisition_line_ids:
            return [(requisition_line.requisition_id, requisition_line.requisition_id.user_id, visited) for
                    requisition_line in self.requisition_line_ids if requisition_line.state not in ('done', 'cancel')]
        else:
            return super(StockMove, self)._get_upstream_documents_and_responsibles(visited)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        for op in self:
            for pr in self.env['subcontract.requisition'].search([('state', '=', 'draft'), ('origin', '=', op.name)]):
                for prline in pr.line_ids.filtered(lambda l: l.product_id.id == op.product_id.id):
                    res[op.id] += prline.product_uom_id._compute_quantity(prline.product_qty, op.product_uom,
                                                                          round=False)
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    subcontract_requisition_id = fields.Many2one('subcontract.requisition', string='Contract', store=True)

    @api.onchange('subcontract_id')
    def _onchange_subcontract_id(self):
        if self.subcontract_id:
            if self.subcontract_id.requisition_id:
                self.subcontract_requisition_id = self.subcontract_id.requisition_id.id
