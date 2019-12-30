# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare
import math


class adding_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    operation_id = fields.Many2one('stock.picking.type', string='Deliver to')

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',default=lambda self: self.inventory_id.analytic_account_id.id)


    def _get_move_values(self, qty, location_id, location_dest_id, out,analytic_account):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'date': self.inventory_id.date,
            'company_id': self.inventory_id.company_id.id,
            'inventory_id': self.inventory_id.id,
            'state': 'confirmed',
            'restrict_partner_id': self.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'analytic_account_id':analytic_account,
            'price_unit':self.force_unit_inventory_cost,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': self.partner_id.id,
            })]
        }

    def _generate_moves(self):
        vals_list = []
        for line in self:
            if float_utils.float_compare(line.theoretical_qty, line.product_qty, precision_rounding=line.product_id.uom_id.rounding) == 0:
                continue
            diff = line.theoretical_qty - line.product_qty
            if diff < 0:  # found more than expected
                vals = line._get_move_values(abs(diff), line.product_id.property_stock_inventory.id, line.location_id.id, False,line.analytic_account_id)
            else:
                vals = line._get_move_values(abs(diff), line.location_id.id, line.product_id.property_stock_inventory.id, True,line.analytic_account_id)
            vals_list.append(vals)
        return self.env['stock.move'].create(vals_list)

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def _get_inventory_lines_values(self):
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
        domain = ' location_id in %s AND quantity != 0 AND active = TRUE'
        args = (tuple(locations.ids),)

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']
        # Empty recordset of products to filter
        products_to_filter = self.env['product.product']

        # case 0: Filter on company
        if self.company_id:
            domain += ' AND company_id = %s'
            args += (self.company_id.id,)

        #case 1: Filter on One owner only or One product for a specific owner
        if self.partner_id:
            domain += ' AND owner_id = %s'
            args += (self.partner_id.id,)
        #case 2: Filter on One Lot/Serial Number
        if self.lot_id:
            domain += ' AND lot_id = %s'
            args += (self.lot_id.id,)
        #case 3: Filter on One product
        if self.product_id:
            domain += ' AND product_id = %s'
            args += (self.product_id.id,)
            products_to_filter |= self.product_id
        #case 4: Filter on A Pack
        if self.package_id:
            domain += ' AND package_id = %s'
            args += (self.package_id.id,)
        #case 5: Filter on One product category + Exahausted Products
        if self.category_id:
            categ_products = Product.search([('categ_id', '=', self.category_id.id)])
            domain += ' AND product_id = ANY (%s)'
            args += (categ_products.ids,)
            products_to_filter |= categ_products

        self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
            FROM stock_quant
            LEFT JOIN product_product
            ON product_product.id = stock_quant.product_id
            WHERE %s
            GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

        for product_data in self.env.cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
        if self.exhausted:
            exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
            vals.extend(exhausted_vals)
        if self.analytic_account_id:
            for v in vals:
                v["analytic_account_id"] = self.analytic_account_id.id
        return vals

    @api.onchange('analytic_account_id')
    @api.constrains('analytic_account_id')
    def set_analytic_account_lines(self):
        for record in self:
            if record.line_ids:
                for line in record.line_ids:
                    line.analytic_account_id = record.analytic_account_id


class Purchase_order_inheriting(models.Model):
    _inherit = 'purchase.order'

    Analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.multi
    @api.onchange('Analytic_id')
    def set_deliver_to(self):
        for rec in self:
            rec.picking_type_id = rec.Analytic_id.operation_id.id

    @api.multi
    def set_analytic_accounts(self):
        for r in self:
            for order in r.order_line:
                order.account_analytic_id = r.Analytic_id.id

    @api.multi
    def action_view_picking(self):
        res = super(Purchase_order_inheriting, self).action_view_picking()
        picking_ids = self.env['stock.picking'].search([('origin', '=', self.name)])
        for pick in picking_ids:
            pick.analytic_id = self.Analytic_id.id
            pick.write({'analytic_id': self.Analytic_id.id})
            # for move in pick.move_ids_without_package:
            #     po_line = self.order_line.filtered(lambda x: x.product_id.id == move.product_id.id)
            #     po_ratio = po_line.product_uom.factor_inv
            #     move_ratio = move.product_uom.factor_inv
            #     if po_line.product_uom.id != move.product_uom.factor_inv and po_ratio != False and move_ratio != False:
            #         if move_ratio == 0:
            #             ratio = po_ratio
            #         else:
            #             ratio = po_ratio/move_ratio
            #         if ratio != False:
            #             move.unit_inventory_cost = move.unit_inventory_cost/ratio

            # pick.unit_inventory_cost = self.unit_inventory_cost
            # raise Warning('KK')
        return res

    @api.multi
    def button_confirm(self):
        # print("KKKKKKKKKLOOOOOOOOO")
        res = super(Purchase_order_inheriting, self).button_confirm()
        picking_ids = self.env['stock.picking'].search([('origin', '=', self.name)])
        # print(picking_ids, 'llllllllllllll')
        for pick in picking_ids:
            pick.analytic_id = self.Analytic_id.id
            pick.write({'analytic_id': self.Analytic_id.id})
            for stock_move in pick.move_ids_without_package:
                for line in self.order_line:
                    if line.product_id.id == stock_move.product_id.id:
                        if stock_move.product_uom_qty == line.product_uom_qty:
                            po_ratio = line.product_uom.factor_inv
                            move_ratio = stock_move.product_uom.factor_inv
                            if line.product_uom.id != stock_move.product_uom.id and po_ratio != False and move_ratio != False:
                                if move_ratio == 0:
                                    ratio = po_ratio
                                else:
                                    ratio = po_ratio / move_ratio
                                if ratio != False:
                                    stock_move.unit_inventory_cost = line.unit_inventory_cost / ratio
                                else:
                                    stock_move.unit_inventory_cost = line.unit_inventory_cost
                            else:
                                stock_move.unit_inventory_cost = line.unit_inventory_cost
                            break
        return res

    # from odoo.addons.sale_stock.models.sale_order import SaleOrder

    # class SaleOrderDisable(models.Model):
    #     _inherit = "sale.order"
    #
    #     def _action_confirm(self):
    #         print('in custom action confirm')
    #         super(SaleOrder, self)._action_confirm()

    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id,
            'analytic': self.Analytic_id.id,
            'default_origin': self.name
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        return result


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    inventory_cost = fields.Float(compute='comp_inventory_cost')
    unit_inventory_cost = fields.Float(compute='comp_inventory_cost')
    line_sequence = fields.Integer(string="Sequence", default=0)

    @api.depends('invoice_line_tax_ids', )
    def comp_inventory_cost(self):

        for rec in self:
            rec.inventory_cost = rec.price_subtotal
            rec.unit_inventory_cost = rec.price_unit
            for tax in rec.invoice_line_tax_ids:
                if tax.include_in_inventory_cost is True and tax.price_include is False:
                    rec.inventory_cost = (tax.amount * rec.price_unit * rec.quantity) / 100 + rec.price_subtotal
                    rec.unit_inventory_cost = rec.price_unit + (tax.amount * rec.price_unit) / 100
                if tax.include_in_inventory_cost is True and tax.price_include is True:
                    rec.inventory_cost = rec.price_unit * rec.quantity
                    rec.unit_inventory_cost = rec.price_unit


class CustInvoiceBills(models.Model):
    _inherit = 'account.invoice'

    # origin = fields.Many2one(comodel_name="purchase.order", string="Source Document",
    #                          help="Reference of the document that produced this invoice.")

    def SetInvPurchase(self):
        context = self.env.context
        if context.get('analytic'):
            return context.get('analytic')

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', default=SetInvPurchase)

    # return self.env['hr.applicant'].search(
    #     [('id', '=', self._context['current_id'])]).test_id.with_context(current_id=self._context['current_id'],
    #                                                                      type='test').action_send_survey()
    # def SetInvPurchase(self):
    #     context = self.env.context
    #     if context.get('analytic'):
    #         return context.get('analytic')

    @api.multi
    @api.onchange('analytic_id')
    def set_deliver_to(self):
        for rec in self:
            rec.picking_type_id = rec.analytic_id.operation_id.id

    @api.multi
    def set_analytic_accounts(self):
        for r in self:
            for order in r.invoice_line_ids:
                order.account_analytic_id = r.analytic_id.id

    @api.multi
    def action_invoice_open(self):

        res = super(CustInvoiceBills, self).action_invoice_open()

        self.move_id.journal_id.update_posted = True
        self.move_id.journal_id.write({'update_posted': True})
        self.move_id.button_cancel()
        for rec in self.move_id.line_ids:
            if not rec.analytic_account_id:
                # print('NOOOOOOOOOOOOOOOO')
                rec.analytic_account_id = self.analytic_id.id
        self.move_id.post()
        self.move_id.journal_id.write({'update_posted': False})
        self.move_id.journal_id.update_posted = False
        # obj = self.env['account.analytic.line'].create({
        #     'account_id': self.analytic_id.id,
        #     'name': rec.account_id.name,
        #     'amount': rec.credit if rec.credit > 0 else rec.debit,
        #     'date': self.date_invoice,
        #     'partner_id': rec.partner_id.id,
        #     'general_account_id': rec.account_id.id,
        #     # 'unit_amount':rec.quantity,
        #     # 'amount':rec.price_subtotal
        # })
        # print(obj,'KKKKKKKKKK')

        return res

    def _prepare_invoice_line_from_po_line(self, line):
        if line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes, line.product_id,
                                                                        line.order_id.partner_id)
        invoice_line = self.env['account.invoice.line']
        date = self.date or self.date_invoice
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context(
                {'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id._convert(
                line.price_unit, self.currency_id, line.company_id, date or fields.Date.today(), round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids,
            'line_sequence': line.line_sequence,
            'inventory_cost': line.inventory_cost,
            'unit_inventory_cost': line.unit_inventory_cost

        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id,
                                                        self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data


class StockPickingWarehouse(models.Model):
    _inherit = 'stock.picking'

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)

    @api.multi
    def button_validate(self):
        res = super(StockPickingWarehouse, self).button_validate()
        stock_journals = self.env['account.journal'].search([('name', '=', 'Stock Journal')])
        # print("stock_journals",stock_journals)
        journal_entry_stock_ids = self.env['account.move'].search(
            [('ref', '=', self.name), ('journal_id', 'in', stock_journals.ids)])
        # print("journal_entry_stock_ids", journal_entry_stock_ids)
        journal_entry_ids = self.env['account.move'].search([('ref', '=', self.name)])
        # print("journal_entry_ids", journal_entry_ids)
        purchase = self.env['purchase.order'].search(
            [ ('name', '=', self.origin)])
        # print("purchase", purchase)
        if self.state == 'done':
            for jornal in journal_entry_ids:
                jornal.journal_id.write({'update_posted': True})
                jornal.journal_id.update_posted = True
                jornal.button_cancel()
                for line in jornal.line_ids:
                    line.analytic_account_id = self.analytic_id.id

        ############################################fix for duplicated entries in tansfers########################################
        # if self.state == 'done':
        #     qty = 0
        #     for jornal in journal_entry_stock_ids:
        #         for l in jornal.line_ids:
        #             orig_deb_cred = l.debit if l.debit != 0 else l.credit
        #             for pur in purchase.order_line:
        #                 qty = (pur.product_qty * (orig_deb_cred / pur.price_subtotal))  # if qty == 0 else qty)
        #                 if not l.reconciled and float_compare(l.debit, qty * (pur.price_subtotal / pur.product_qty),
        #                                  precision_digits=1) == 0 and l.name == pur.name:
        #                     l.with_context(check_move_validity=False).debit = qty * (
        #                             pur.inventory_cost / pur.product_qty)
        #                 if not l.reconciled and float_compare(l.credit, qty * (pur.price_subtotal / pur.product_qty),
        #                                  precision_digits=1) == 0 and l.name == pur.name:
        #                     l.with_context(check_move_validity=False).credit = qty * (
        #                             pur.inventory_cost / pur.product_qty)
        #####################################end########################################################
        # jornal.post()
        # jornal.journal_id.write({'update_posted': False})
        # jornal.journal_id.update_posted = False

        # purchase_id = self.env['purchase.order'].search(
        #     ['|', ('name', '=', self.origin), ('name', '=', self.origin1.name)], limit=1)
        # obj=self.env['account.analytic.line'].create({
        #     'account_id': self.analytic_id.id,
        #     'name': purchase_id.name+line.account_id.name,
        #     'amount': -line.credit if line.credit>0 else line.debit,
        #     # 'unit_amount':rec.quantity,
        #     'date': self.scheduled_date,
        #     'partner_id': self.partner_id.id,
        #     'general_account_id': line.account_id.id
        # })
        # print('objjjjjjjjjjjjjjjjj',obj)
        # if self.analytic_account.id:
        return res


class StockImmediateTransferInherit(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    @api.multi
    def process(self):
        res = super(StockImmediateTransferInherit, self).process()
        for picking in self.pick_ids:
            purchase = self.env['purchase.order'].search(
                [ ('name', '=', picking.origin)])
            stock_journals = self.env['account.journal'].search([('name', '=', 'Stock Journal')])
            journal_entry_stock_ids = self.env['account.move'].search(
                [('ref', '=', picking.name), ('journal_id', 'in', stock_journals.ids)])
            journal_entry_ids = self.env['account.move'].search([('ref', '=', picking.name)])
            if picking.state == 'done':
                for jornal in journal_entry_ids:
                    jornal.journal_id.write({'update_posted': True})
                    # print("VVVVVVVVVVVVVVCCCCCC",jornal.journal_id.update_posted)
                    jornal.journal_id.update_posted = True
                    jornal.button_cancel()
                    for line in jornal.line_ids:
                        line.analytic_account_id = picking.analytic_id.id

                    ####################
            # if self.state == 'done':
            qty = 0
            #######################Journal Entries doubled taxes########################
            # for jornal in journal_entry_stock_ids:
            #     for l in jornal.line_ids:
            #         print("debit: ",l.debit,"credit: ",l.credit)
            #         orig_deb_cred = l.debit if l.debit != 0 else l.credit
            #         for pur in purchase.order_line:
            #             qty = (pur.product_qty * (orig_deb_cred / pur.price_subtotal))  # if qty == 0 else qty)
            #             if not l.reconciled and float_compare(l.debit, qty * (pur.price_subtotal / pur.product_qty),
            #                              precision_digits=1) == 0 and l.name == pur.name:
            #                 l.with_context(check_move_validity=False).debit = qty * (
            #                         pur.inventory_cost / pur.product_qty)
            #                 print("debit: ", l.debit, "credit: ", l.credit)
            #             if not l.reconciled and float_compare(l.credit, qty * (pur.price_subtotal / pur.product_qty),
            #                              precision_digits=1) == 0 and l.name == pur.name:
            #                 l.with_context(check_move_validity=False).credit = qty * (
            #                         pur.inventory_cost / pur.product_qty)
            #                 print("debit: ", l.debit, "credit: ", l.credit)

            #####################End Journal Entries doubled digits ##############################
            # jornal.post()
            # jornal.journal_id.update_posted = False
            # jornal.journal_id.write({'update_posted': False})
            # print("VVVVVVVVVVVVVVCCCCCC", jornal.journal_id.update_posted)

            # purchase_id = self.env['purchase.order'].search(
            #     ['|', ('name', '=', picking.origin), ('name', '=', picking.origin1.name)], limit=1)
            # obj=self.env['account.analytic.line'].create({
            #     'account_id': picking.analytic_id.id,
            #     'name': purchase_id.name + line.account_id.name,
            #     'amount': -line.credit if line.credit>0 else line.debit,
            #     'date': picking.scheduled_date,
            #     'partner_id': picking.partner_id.id,
            #     'general_account_id': line.account_id.id
            # })
            # print(line.account_id.id,'objjjjjjjjjjjjjjjjj', obj)
        return res


class StockBackorderConfirmationInherit(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.multi
    def process(self):
        res = super(StockBackorderConfirmationInherit, self).process()
        for picking in self.pick_ids:
            purchase = self.env['purchase.order'].search(
                [('name', '=', picking.origin)])
            journal_entry_ids = self.env['account.move'].search([('ref', '=', picking.name)])
            stock_journals = self.env['account.journal'].search([('name', '=', 'Stock Journal')])
            journal_entry_stock_ids = self.env['account.move'].search(
                [('ref', '=', picking.name), ('journal_id', 'in', stock_journals.ids)])
            if picking.state == 'done':
                for jornal in journal_entry_ids:
                    jornal.journal_id.write({'update_posted': True})
                    jornal.journal_id.update_posted = True
                    jornal.button_cancel()
                    for line in jornal.line_ids:
                        line.analytic_account_id = picking.analytic_id.id

            # if self.state == 'done':
            ############################################# bug start###############################################
            # qty = 0
            # for jornal in journal_entry_stock_ids:
            #     for l in jornal.line_ids:
            #         orig_deb_cred = l.debit if l.debit != 0 else l.credit
            #         for pur in purchase.order_line:
            #             qty =  (pur.product_qty * (orig_deb_cred / pur.price_subtotal))# if qty == 0 else qty)
            #             if not l.reconciled and float_compare(l.debit, qty * (pur.price_subtotal / pur.product_qty),
            #                              precision_digits=1) == 0 and l.name == pur.name:
            #                 l.with_context(check_move_validity=False).debit = qty * (
            #                         pur.inventory_cost / pur.product_qty)
            #             if not l.reconciled and float_compare(l.credit, qty * (pur.price_subtotal / pur.product_qty),
            #                              precision_digits=1) == 0 and l.name == pur.name:
            #                 l.with_context(check_move_validity=False).credit = qty * (
            #                         pur.inventory_cost / pur.product_qty)
            #
            # ############################################end######################################################3
            # jornal.post()
            # jornal.journal_id.write({'update_posted': False})
            # jornal.journal_id.update_posted = False

            # purchase_id = self.env['purchase.order'].search(
            #     ['|', ('name', '=', picking.origin), ('name', '=', picking.origin1.name)], limit=1)
            # obj = self.env['account.analytic.line'].create({
            #     'account_id': picking.analytic_id.id,
            #     'name': purchase_id.name + line.account_id.name,
            #     'amount': -line.credit if line.credit>0 else line.debit,
            #     'date': picking.scheduled_date,
            #     'partner_id': picking.partner_id.id,
            #     'general_account_id': line.account_id.id
            # })
            # print('objjjjjjjjjjjjjjjjj', obj)
        return res


class AccouuntTaxInherit(models.Model):
    _inherit = 'account.tax'

    include_in_inventory_cost = fields.Boolean(default=False)
    TAX_TYPES = [('قوي عاملة', 'قوي عاملة'),
                 ('تامين اعمال', 'تامين اعمال'),
                 ('تامينات اجتماعية', 'تامينات اجتماعية'),
                 ('تأمين محتجز', 'تأمين محتجز'),
                 ('أ.ت.ص', 'أ.ت.ص'),
                 ('دفعات مقدمة', 'دفعات مقدمة'), ]
    tax_type = fields.Selection(string="Tax Type", selection=TAX_TYPES, default=TAX_TYPES[0][0])


class PurchaseOrderLINE(models.Model):
    _inherit = 'purchase.order.line'

    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    inventory_cost = fields.Float(compute='comp_inventory_cost')
    unit_inventory_cost = fields.Float(compute='comp_inventory_cost')

    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #         taxes = line.taxes_id.compute_all(
    #             vals['price_unit'],
    #             vals['currency_id'],
    #             vals['product_qty'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })

    # @api.onchange('taxes_id')
    @api.depends('taxes_id', 'price_subtotal')
    def comp_inventory_cost(self):

        for rec in self:
            rec.inventory_cost = math.floor(rec.price_unit * rec.product_qty * 1000) / 1000
            rec.unit_inventory_cost = rec.price_unit
            for tax in rec.taxes_id:
                if tax.include_in_inventory_cost is True and tax.price_include is False:
                    rec.inventory_cost = (tax.amount * rec.price_unit * rec.product_qty) / 100 + rec.price_subtotal
                    rec.unit_inventory_cost = rec.price_unit + (tax.amount * rec.price_unit) / 100
                if tax.include_in_inventory_cost is True and tax.price_include is True:
                    rec.inventory_cost = rec.price_unit * rec.product_qty
                    rec.unit_inventory_cost = rec.price_unit
                # else:
                #     rec.inventory_cost = rec.price_subtotal
                #     rec.unit_inventory_cost = rec.price_unit


class StockReturnLineInventoryCost(models.TransientModel):
    _inherit = 'stock.return.picking.line'
    unit_inventory_cost = fields.Float()


class StockReturnInventoryCost(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super(StockReturnInventoryCost, self).default_get(fields)
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking and 'product_return_moves' in res:
            for move in res['product_return_moves']:
                move[2]['unit_inventory_cost'] = self.env['stock.move'].browse(move[2]['move_id']).unit_inventory_cost
                move[2]['price_unit'] = self.env['stock.move'].browse(move[2]['move_id']).price_unit
        return res

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = res = super(StockReturnInventoryCost, self)._prepare_move_default_values(return_line, new_picking)
        vals['unit_inventory_cost'] = vals['price_unit'] = return_line.unit_inventory_cost * -1
        return vals


class Company(models.Model):
    _inherit = "res.company"
    advance_payment = fields.Many2one('account.account', 'الدفعة المقدمة')
    Balance_due = fields.Many2one('account.account', 'الرصيد المستحق')
    payments = fields.Many2one('account.account', 'الدفعات')
    reserved_insurance = fields.Many2one('account.account', 'رصيد التامين المحجوز')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    advance_payment = fields.Many2one('account.account',
                                      string='الدفعة المقدمة',
                                      domain=[('deprecated', '=', False)],
                                      related="company_id.advance_payment",
                                      readonly=False)
    Balance_due = fields.Many2one('account.account',
                                  string='الرصيد المستحق',
                                  domain=[('deprecated', '=', False)],
                                  related="company_id.Balance_due",
                                  readonly=False)
    payments = fields.Many2one('account.account',
                               string='الدفعات',
                               domain=[('deprecated', '=', False)],
                               related="company_id.payments",
                               readonly=False)
    reserved_insurance = fields.Many2one('account.account',
                                         string='رصيد التامين المحجوز',
                                         domain=[('deprecated', '=', False)],
                                         related="company_id.reserved_insurance",
                                         readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        tmp_advance_payment = params.get_param('advance_payment')
        tmp_Balance_due = params.get_param('Balance_due')
        tmp_payments = params.get_param('payments')
        tmp_reserved_insurance = params.get_param('reserved_insurance')

        res.update(
            advance_payment=tmp_advance_payment and int(tmp_advance_payment) or '',
            Balance_due=tmp_Balance_due and int(tmp_Balance_due) or '',
            payments=tmp_payments and int(tmp_payments) or '',
            reserved_insurance=tmp_reserved_insurance and int(tmp_reserved_insurance) or '',
        )
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('advance_payment',
                                                         self.advance_payment and self.advance_payment.id or '')
        self.env['ir.config_parameter'].sudo().set_param('Balance_due', self.Balance_due and self.Balance_due.id or '')
        self.env['ir.config_parameter'].sudo().set_param('payments', self.payments and self.payments.id or '')
        self.env['ir.config_parameter'].sudo().set_param('reserved_insurance',
                                                         self.reserved_insurance and self.reserved_insurance.id or '')

        self.company_id.advance_payment = self.advance_payment
        self.company_id.Balance_due = self.Balance_due
        self.company_id.payments = self.payments
        self.company_id.reserved_insurance = self.reserved_insurance


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def get_bank_statement_line_data(self, st_line_ids, excluded_ids=None):
        """ Returns the data required to display a reconciliation widget, for
            each statement line in self

            :param st_line_id: ids of the statement lines
            :param excluded_ids: optional move lines ids excluded from the
                result
        """
        excluded_ids = excluded_ids or []

        # Make a search to preserve the table's order.
        bank_statement_lines = self.env['account.bank.statement.line'].search([('id', 'in', st_line_ids)])
        reconcile_model = self.env['account.reconcile.model'].search([('rule_type', '!=', 'writeoff_button')])

        # Search for missing partners when opening the reconciliation widget.
        partner_map = self._get_bank_statement_line_partners(bank_statement_lines)

        matching_amls = reconcile_model._apply_rules(bank_statement_lines, excluded_ids=excluded_ids,
                                                     partner_map=partner_map)

        results = {
            'lines': [],
            'value_min': 0,
            'value_max': len(bank_statement_lines),
            'reconciled_aml_ids': [],
        }

        # Iterate on st_lines to keep the same order in the results list.
        bank_statements_left = self.env['account.bank.statement']
        for line in bank_statement_lines:
            if matching_amls[line.id].get('status') == 'reconciled':
                reconciled_move_lines = matching_amls[line.id].get('reconciled_lines')
                results['value_min'] += 1
                results['reconciled_aml_ids'] += reconciled_move_lines and reconciled_move_lines.ids or []
            else:
                aml_ids = matching_amls[line.id]['aml_ids']
                bank_statements_left += line.statement_id
                target_currency = line.currency_id or line.journal_id.currency_id or line.journal_id.company_id.currency_id

                amls = aml_ids and self.env['account.move.line'].browse(aml_ids)
                line_vals = {
                    'analytic_account_id': line.analytic_account_id.id,
                    'analytic_account_name': line.analytic_account_id.name,
                    'st_line': self._get_statement_line(line),
                    'reconciliation_proposition': aml_ids and self._prepare_move_lines(amls,
                                                                                       target_currency=target_currency,
                                                                                       target_date=line.date) or [],
                    'model_id': matching_amls[line.id].get('model') and matching_amls[line.id]['model'].id,
                    'write_off': matching_amls[line.id].get('status') == 'write_off',
                }
                if not line.partner_id and partner_map.get(line.id):
                    partner = self.env['res.partner'].browse(partner_map[line.id])
                    line_vals.update({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                    })
                results['lines'].append(line_vals)

        return results
