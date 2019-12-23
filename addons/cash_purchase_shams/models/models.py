# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class cash_purchase_shams(models.Model):
    _name = 'cash.purchase.shams'


    default_vendor_id = fields.Many2one('res.partner', string='Default Vendor', company_dependent=True)
    purchase_limit = fields.Float(company_dependent=True)

class PurchaseOrderInventory(models.Model):
    _inherit = 'purchase.order'

    def _default_vendor_id(self):
        if self.env.user.has_group('cash_purchase_shams.group_cash_purchase'):
            setting_id = self.env['cash.purchase.shams'].search([])
            return setting_id.default_vendor_id.id
        # else:
        #     return

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, default=_default_vendor_id,
                                 change_default=True, track_visibility='always',
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")


    # @api.onchange('id')
    # def confirm_orders(self):
    #     if self.env.user.has_group('cash_purchase_shams.group_cash_purchase'):
    #         setting_id = self.env['cash.purchase.shams'].search([])
    #         # raise Warning('HHHHHHHHHHHHHHh')
    #         print(self.amount_total, 'FFFFFF', setting_id.purchase_limit)
    #         if self.amount_total > setting_id.purchase_limit:
    #             raise UserError('Cannot Confirm This Amount')
    #         else:
    #             self.button_confirm()


    @api.multi
    def button_confirm(self):
        print('In confirmmmmmmmmmmm function')
        # raise Warning('HHHHHHHHHHHHHHh')
        if self.env.user.has_group('cash_purchase_shams.group_cash_purchase'):
            setting_id = self.env['cash.purchase.shams'].search([])
            # raise Warning('HHHHHHHHHHHHHHh')
            print(self.amount_total,'FFFFFF',setting_id.purchase_limit)
            if self.amount_total > setting_id.purchase_limit:
                print('SSSSSSSSSSSSSSSS')
                raise UserError('Cannot Confirm This Amount')
            else:
                res = super(PurchaseOrderInventory, self).button_confirm()
                return res
        else:
            res = super(PurchaseOrderInventory, self).button_confirm()
            return res

    # @api.multi
    # def button_confirm(self):
    #     if self.env.user.has_group('cash_purchase_shams.group_cash_purchase'):
    #         setting_id = self.env['cash.purchase.shams'].search([])
    #         print(self.amount_total,'FFFFFF',setting_id.purchase_limit)
    #         if self.amount_total > setting_id.purchase_limit:
    #             raise UserError('Cannot Confirm This Amount')
    #     else:
    #         for order in self:
    #             if order.state not in ['draft', 'sent']:
    #                 continue
    #             order._add_supplier_to_product()
    #             # Deal with double validation process
    #             if order.company_id.po_double_validation == 'one_step' \
    #                     or (order.company_id.po_double_validation == 'two_step' \
    #                         and order.amount_total < self.env.user.company_id.currency_id._convert(
    #                         order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
    #                         order.date_order or fields.Date.today())) \
    #                     or order.user_has_groups('purchase.group_purchase_manager'):
    #                 order.button_approve()
    #             else:
    #                 order.write({'state': 'to approve'})
    #         return True

    @api.model
    def create(self, vals):
        if self.env.user.has_group('cash_purchase_shams.group_cash_purchase'):
            #     raise UserError('Cannot Confirm This Amount')
            vals['state'] = 'approved'
            res = super(PurchaseOrderInventory, self).create(vals)
            return res
        else:
            res = super(PurchaseOrderInventory, self).create(vals)
            return res

    # @api.depends('order_line.price_total')
    # def _amount_all(self):
    #     for order in self:
    #         amount_untaxed = amount_tax = 0.0
    #         for line in order.order_line:
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_tax
    #         order.update({
    #             'amount_untaxed': order.currency_id.round(amount_untaxed),
    #             'amount_tax': order.currency_id.round(amount_tax),
    #             'amount_total': amount_untaxed + amount_tax,
    #         })



