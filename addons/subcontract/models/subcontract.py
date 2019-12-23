# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, Warning
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class SubContractorCategory(models.Model):
    _name = "subcontract.category"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Char(string="Description")
    parent = fields.Char(string="Parent")


class SubContractorCode(models.Model):
    _name = "subcontract.code"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Char(string="Description")
    parent = fields.Char(string="Parent")


class SubcontractOrder(models.Model):
    _name = "subcontract.order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Subcontract"
    _order = 'date_order desc, id desc'

    @api.multi
    @api.onchange('account_analytic_id')
    def set_deliver_to(self):
        for rec in self:
            rec.picking_type_id = rec.account_analytic_id.operation_id.id

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.date_planned', 'date_order')
    def _compute_date_planned(self):
        for order in self:
            min_date = False
            for line in order.order_line:
                if not min_date or line.date_planned < min_date:
                    min_date = line.date_planned
            if min_date:
                order.date_planned = min_date
            else:
                order.date_planned = order.date_order

    @api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('subcontract', 'done'):
                order.invoice_status = 'no'
                continue
            if any(float_compare(line.qty_invoiced,
                                 line.product_qty if line.product_id.subcontract_method == 'subcontract' else line.qty_received,
                                 precision_digits=precision) == -1 for line in order.order_line):
                order.invoice_status = 'to invoice'
            elif all(float_compare(line.qty_invoiced,
                                   line.product_qty if line.product_id.subcontract_method == 'subcontract' else line.qty_received,
                                   precision_digits=precision) >= 0 for line in order.order_line) and order.invoice_ids:
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    @api.depends('order_line.invoice_lines.invoice_id')
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    is_exceed = fields.Boolean(default=False)

    READONLY_STATES = {
        'subcontract': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')

    origin = fields.Char('Source Document', copy=False,
                         help="Reference of the document that generated this subcontract order "
                              "request (e.g. a sales order)")
    partner_ref = fields.Char('Subcontractor Reference', copy=False,
                              help="Reference of the sales order or bid sent by the vendor. "
                                   "It's used to do the matching when you receive the "
                                   "products as this reference is usually written on the "
                                   "delivery order sent by your vendor.")
    date_order = fields.Datetime('Order Date', required=True, index=True, copy=False, states=READONLY_STATES,
                                 default=fields.Datetime.now, \
                                 help="Depicts the date where the Quotation should be validated and converted into a subcontract order.")
    date_approve = fields.Date('Approval Date', readonly=1, index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Subcontractor', required=True, states=READONLY_STATES,
                                 help="You can find a subcontractor by its Name, TIN, Email or Internal Reference.",
                                 domain=[('subcontractor', '=', True)])
    dest_address_id = fields.Many2one('res.partner', string='Drop Ship Address', states=READONLY_STATES,
                                      help="Put an address if you want to deliver directly from the vendor to the customer. "
                                           "Otherwise, keep empty to deliver to your own company.")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection(
        [('draft', 'RFQ'),('waiting_rfq_approve','Waiting RFQ Approval'),('rfq_approved','Approved'), ('sent', 'RFQ Sent'), ('to approve', 'To Approve'), ('subcontract', 'Subcontract Order'),
         ('done', 'Locked'), ('cancel', 'Cancelled')], string='Status', readonly=True, index=True, copy=False,
        default='draft', track_visibility='onchange')

    order_line = fields.One2many('subcontract.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
                                 copy=True)

    notes = fields.Text('Terms and Conditions')
    invoice_count = fields.Integer(compute="_compute_invoice", string='Bill Count', copy=False, default=0, store=True)

    invoice_ids = fields.Many2many('account.invoice', compute="_compute_invoice", string='Bills', copy=False,
                                   store=True)

    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'No Bill to Receive'),
    ], string='Billing Status', compute='_get_invoiced', store=True, readonly=True, copy=False, default='no')

    date_planned = fields.Datetime(string='Scheduled Date', compute='_compute_date_planned', store=True, index=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_amount_all', store=True, readonly=True,
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', compute='_amount_all',
                                 store=True, readonly=True, )
    amount_total = fields.Monetary(string='Total', compute='_amount_all', store=True, readonly=True, )
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterm', states={'done': [('readonly', True)]},
                                  help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
    product_id = fields.Many2one('product.product', related='order_line.product_id', string='Product', readonly=False)
    user_id = fields.Many2one('res.users', string='Representative', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES,
                                 default=lambda self: self.env.user.company_id.id)
    # New fields subcontractor
    account_analytic_id = fields.Many2one('account.analytic.account', string="Project")
    category = fields.Many2one('subcontract.category', string="Category")

    @api.multi
    def button_confirmation(self):
        for order in self:
            if order.requisition_id:
                flag_exceed = False
                for line in order.order_line:
                    requisition_line_ids = order.requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id and r.sequence == line.line_sequence)
                    requisition_line_ids._compute_ordered_qty()
                    requisition_line_ids._compute_ordered_price()
                    for scr_line in requisition_line_ids:
                        if scr_line.product_qty < scr_line.qty_ordered + scr_line.previ_qty + line.product_qty:
                            line.is_coloring = 't'
                            flag_exceed = True
                            # line.write({'is_coloring':'t'})
                            # print('color', scr_line.is_coloring)
                            # action = self.env.ref('calendar.action_calendar_event').read()[0]
                            # action['context'] = {
                            #     'model_id': self.id,
                            # }
                            # return action
                            # return {
                            #     'name': 'Confirm',
                            #     'type': 'ir.actions.act_window',
                            #     'view_type': 'form',
                            #     'view_mode': 'form',
                            #     'src_model': 'subcontract.order',
                            #     'res_model': 'pop.wizard.confirm',
                            #     'target': 'new',
                            #     'context': {'current_id': self.id},
                            #     'views': [(self.env.ref('subcontract.popup_wiz_view').id,
                            #                'form')],
                            # }
                        # else:
                        #     return self.button_confirm()
                            # raise Warning(
                            #     _("You shouldn't exceed the Contract quantity, please contact your administrator"))
                        if (scr_line.product_qty * scr_line.price_unit) < scr_line.price_ordered:
                            line.is_coloring = 't'
                            flag_exceed = True
                            # line.write({'is_coloring': 't'})
                            # print('color', scr_line.is_coloring)
                            # return {
                            #     'name': 'Confirm',
                            #     'type': 'ir.actions.act_window',
                            #     'view_type': 'form',
                            #     'view_mode': 'form',
                            #     'src_model': 'subcontract.order',
                            #     'res_model': 'pop.wizard.confirm',
                            #     'target': 'new',
                            #     'context': {'current_id': self.id},
                            #     'views': [(self.env.ref('subcontract.popup_wiz_view').id,
                            #                'form')],
                            # }
                if flag_exceed:
                    return {
                        'name': 'Confirm',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'src_model': 'subcontract.order',
                        'res_model': 'pop.wizard.confirm',
                        'target': 'new',
                        'context': {'current_id': self.id},
                        'views': [(self.env.ref('subcontract.popup_wiz_view').id,
                                   'form')],
                    }
                else:
                    return self.button_confirm()
                    # return self.env['hr.applicant'].search([('id', '=',self._context['current_id'])]).action_start_survey()
                            # raise Warning(_("You shouldn't exceed the Contract amount, please contact your administrator"))
        # res = super(SubcontractOrder, self).button_confirm()
        # return res

    # context="{'model_id': active_id}"

    def send_rfq_approval(self):
        self.state = "waiting_rfq_approve"

    def confirm_rfq_approval(self):
        if self.user_has_groups('subcontract.group_manage_rfq_approval'):
            self.state = "rfq_approved"

            # for order in self:
            #     if order.requisition_id:
            #         for line in order.order_line:
            #             requisition_line_ids = order.requisition_id.line_ids.filtered(
            #                 lambda r: r.product_id == line.product_id and r.sequence == line.line_sequence)
            #             requisition_line_ids._compute_ordered_qty()
            #             requisition_line_ids._compute_ordered_price()
            #             for scr_line in requisition_line_ids:
            #                 if scr_line.product_qty < scr_line.qty_ordered:
            #                     order.write({'is_exceed':True})
            #                     print(order.is_exceed,'EXCEED')
            #                 if (scr_line.product_qty * scr_line.price_unit) < scr_line.price_ordered:
            #                     order.write({'is_exceed': True})
            #                     print(order.is_exceed, 'EXCEEDed')
        else:
            raise Warning("You don't have permission to approve. please enable from User Settings")

    def _compute_access_url(self):
        super(SubcontractOrder, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/subcontract/%s' % (order.id)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('partner_ref', operator, name)]
        subcontract_order_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(subcontract_order_ids).name_get()

    @api.multi
    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = []
        for co in self:
            name = co.name
            if co.partner_ref:
                name += ' (' + co.partner_ref + ')'
            if self.env.context.get('show_total_amount') and co.amount_total:
                name += ': ' + formatLang(self.env, co.amount_total, currency_obj=co.currency_id)
            result.append((co.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('subcontract.order') or '/'
        return super(SubcontractOrder, self).create(vals)

    @api.multi
    def unlink(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a subcontract order, you must cancel it first.'))
        return super(SubcontractOrder, self).unlink()

    @api.multi
    def copy(self, default=None):
        new_co = super(SubcontractOrder, self).copy(default=default)
        for line in new_co.order_line:
            seller = line.product_id._select_seller(
                partner_id=line.partner_id, quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(), uom_id=line.product_uom)
            line.date_planned = line._get_date_planned(seller)
        return new_co

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'subcontract':
            return 'subcontract.mt_rfq_approved'
        elif 'state' in init_values and self.state == 'to approve':
            return 'subcontract.mt_rfq_confirmed'
        elif 'state' in init_values and self.state == 'done':
            return 'subcontract.mt_rfq_done'
        return super(SubcontractOrder, self)._track_subtype(init_values)

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.fiscal_position_id = False
            self.payment_term_id = False
            self.currency_id = False
        else:
            self.fiscal_position_id = self.env['account.fiscal.position'].with_context(
                company_id=self.company_id.id).get_fiscal_position(self.partner_id.id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            self.currency_id = self.partner_id.property_subcontract_currency_id.id or self.env.user.company_id.currency_id.id
        return {}

    @api.onchange('fiscal_position_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the PO.
        """
        for order in self:
            order.order_line._compute_tax_id()

    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        if not self.partner_id:
            return
        warning = {}
        title = False
        message = False

        partner = self.partner_id

        # If partner has no warning, check its company
        if partner.subcontract_warn == 'no-message' and partner.parent_id:
            partner = partner.parent_id

        if partner.subcontract_warn and partner.subcontract_warn != 'no-message':
            # Block if partner only has warning but parent company is blocked
            if partner.subcontract_warn != 'block' and partner.parent_id and partner.parent_id.subcontract_warn == 'block':
                partner = partner.parent_id
            title = _("Warning for %s") % partner.name
            message = partner.subcontract_warn_msg
            warning = {
                'title': title,
                'message': message
            }
            if partner.subcontract_warn == 'block':
                self.update({'partner_id': False})
            return {'warning': warning}
        return {}

    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi subcontract template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('subcontract', 'email_template_edi_subcontract')[1]
            else:
                template_id = ir_model_data.get_object_reference('subcontract', 'email_template_edi_subcontract_done')[
                    1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'subcontract.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
        return super(SubcontractOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    @api.multi
    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('subcontract.report_subcontract_quotation').report_action(self)

    @api.multi
    def button_approve(self, force=False):
        self.write({'state': 'subcontract', 'date_approve': fields.Date.context_today(self)})
        self.filtered(lambda p: p.company_id.co_lock == 'lock').write({'state': 'done'})
        return {}

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'rfq_approved', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.co_double_validation == 'one_step' \
                    or (order.company_id.co_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                        order.company_id.co_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('subcontract.group_subcontract_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    @api.multi
    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_(
                        "Unable to cancel this subcontract order. You must first cancel the related progress invoice."))

        self.write({'state': 'cancel'})

    @api.multi
    def button_unlock(self):
        self.write({'state': 'subcontract'})

    @api.multi
    def button_done(self):
        self.write({'state': 'done'})

    @api.multi
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                currency = partner.property_subcontract_currency_id or self.env.user.company_id.currency_id
                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(
                        line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'product_uom': line.product_uom.id,
                    'min_qty': 0.0,
                    'price': self.currency_id._convert(line.price_unit, currency, line.company_id,
                                                       line.date_order or fields.Date.today(), round=False),
                    'currency_id': currency.id,
                    'delay': 0,
                }
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break

    # todo:need to create, check invoice
    @api.multi
    def action_view_invoice(self):

        '''
        This function returns an action that display existing progress invoice of given subcontract order ids.
        When only one found, show the progress invoice immediately.
        '''
        action = self.env.ref('progress_invoice.action_progress_invoice')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_subcontract_id': self.id,
            'default_account_analytic_id': self.account_analytic_id.id,
            'default_analytic_id': self.account_analytic_id.id,
            'default_partner_id': self.partner_id.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'journal_type': 'purchase',
            'default_progress_invoice': True,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('progress_invoice.invoice_progress_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        return result

    @api.multi
    def action_set_date_planned(self):
        for order in self:
            order.order_line.update({'date_planned': order.date_planned})


class PopWizardConfirm(models.TransientModel):
    _name = 'pop.wizard.confirm'

    name = fields.Integer()

    def action_confirm(self):
        return self.env['subcontract.order'].search([('id', '=', self._context['current_id'])]).button_confirm()



class SubcontractOrderLine(models.Model):
    _name = "subcontract.order.line"
    _description = 'Subcontract Line'
    _order = 'order_id, sequence, id'

    @api.multi
    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.supplier_taxes_id.filtered(
                lambda r: not line.company_id or r.company_id == line.company_id)
            line.taxes_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id) if fpos else taxes

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the subcontract orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    if inv_line.invoice_id.type == 'in_invoice':
                        qty += inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.invoice_id.type == 'in_refund':
                        qty -= inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    #
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    product_image = fields.Binary(
        'Product Image', related="product_id.image", readonly=False,
        help="Non-stored related field to allow portal user to see the image of the product he has ordered")
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', store=True)
    #
    price_total = fields.Monetary(string='Total', compute='_compute_amount', store=True)
    #
    price_tax = fields.Float(string='Tax', compute='_compute_amount', store=True)
    #

    order_id = fields.Many2one('subcontract.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True,
                                 readonly=True)
    state = fields.Selection(related='order_id.state', store=True)

    invoice_lines = fields.One2many('account.invoice.line', 'subcontract_line_id', string="Bill Lines", readonly=True,
                                    copy=False)

    # Replace by invoiced Qty
    qty_invoiced = fields.Float(string="Billed Qty", compute='_compute_qty_invoiced',
                                digits=dp.get_precision('Product Unit of Measure'), store=True)
    #
    qty_received = fields.Float(string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), copy=False)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    cost_code_id = fields.Many2one('subcontract.code', string="Cost Code")
    previ_qty = fields.Float()
    previ_amount = fields.Float()
    line_sequence = fields.Integer(string="Sequence", default=0)
    # is_coloring = fields.Boolean(default=False)
    is_coloring = fields.Selection([
        ('t', 'True'), ('f', 'False')], default='f', )#compute='comp_color'

    # @api.multi
    # def comp_color(self):
    #     for rec in self:
    #         if rec.product_qty < rec.qty_ordered:
    #             rec.is_coloring = 't'
    #         else:
    #             rec.is_coloring = 'f'

    # my_total = fields.Float(string='Total', compute='CalcTotal')
    #
    # @api.multi
    # @api.depends('price_unit')
    # def CalcTotal(self):
    #     for re in self:
    #         re.my_total = re.price_unit * re.product_qty


    @api.model
    def create(self, values):
        line = super(SubcontractOrderLine, self).create(values)
        if line.order_id.state == 'subcontract':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)
        return line

    @api.multi
    def write(self, values):
        if 'product_qty' in values:
            for line in self:
                if line.order_id.state == 'subcontract':
                    line.order_id.message_post_with_view('subcontract.track_co_line_template',
                                                         values={'line': line, 'product_qty': values['product_qty']},
                                                         subtype_id=self.env.ref('mail.mt_note').id)
        return super(SubcontractOrderLine, self).write(values)

    @api.multi
    def unlink(self):
        for line in self:
            if line.order_id.state in ['subcontract', 'done']:
                raise UserError(_('Cannot delete a subcontract order line which is in state \'%s\'.') % (line.state,))
        return super(SubcontractOrderLine, self).unlink()

    @api.model
    def _get_date_planned(self, seller, co=False):
        """Return the datetime value to use as Schedule Date (``date_planned``) for
           CO Lines that correspond to the given product.seller_ids,
           when ordered at `date_order_str`.

           :param Model seller: used to fetch the delivery delay (if no seller
                                is provided, the delay is 0)
           :param Model co: subcontract.order, necessary only if the CO line is
                            not yet attached to a CO.
           :rtype: datetime
           :return: desired Schedule Date for the CO line
        """
        date_order = co.date_order if co else self.order_id.date_order
        if date_order:
            return date_order + relativedelta(days=seller.delay if seller else 0)
        else:
            return datetime.today() + relativedelta(days=seller.delay if seller else 0)

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_subcontract:
            self.name += '\n' + product_lang.description_subcontract

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(
                self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    @api.onchange('product_id')
    def onchange_product_id_warning(self):
        if not self.product_id:
            return
        warning = {}
        title = False
        message = False

        product_info = self.product_id

        if product_info.subcontract_line_warn != 'no-message':
            title = _("Warning for %s") % product_info.name
            message = product_info.subcontract_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product_info.subcontract_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        return {}

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            if self.product_id.seller_ids.filtered(lambda s: s.name.id == self.partner_id.id):
                self.price_unit = 0.0
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

    @api.multi
    @api.depends('product_uom', 'product_qty', 'product_id.uom_id')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id.uom_id != line.product_uom:
                line.product_uom_qty = line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id)
            else:
                line.product_uom_qty = line.product_qty

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return

        seller_min_qty = self.product_id.seller_ids \
            .filtered(lambda r: r.name == self.order_id.partner_id) \
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom = seller_min_qty[0].product_uom
        else:
            self.product_qty = 1.0
