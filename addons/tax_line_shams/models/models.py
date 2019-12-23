# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceTax(models.Model):
    _name = "tax_line.purchase.tax"
    _inherit = "account.invoice.tax"
    purchase_id = fields.Many2one('purchase.order', string='Purchase',)
    account_id = fields.Many2one('account.account', string='Tax Account', required=False, domain=[('deprecated', '=', False)])




class tax_line_shams(models.Model):
    _inherit = 'purchase.order'

    tax_line_ids = fields.One2many('tax_line.purchase.tax', 'purchase_id', string='Tax Lines', oldname='tax_line',
                                   readonly=True, states={'draft': [('readonly', False)]}, copy=True)



    @api.onchange('order_line')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return


    def _prepare_tax_line_vals(self, line, tax):

        vals = {
            'purchase_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            # 'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
            'analytic_tag_ids': tax['analytic'] and line.analytic_tag_ids.ids or False,
        }

        # If the taxes generate moves on the same financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of) the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not vals.get('account_analytic_id') and line.account_analytic_id:
            vals['account_analytic_id'] = line.account_analytic_id.id
        return vals

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.order_line:
            # if not line.account_id:
            #     continue
            price_unit = line.price_unit #* (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price_unit, self.currency_id, line.product_qty, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_keys(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped


class custom_account_tax(models.Model):
    _inherit = 'account.tax'

    def get_grouping_keys(self, invoice_tax_val):
        """ Returns a string that will be used to group account.invoice.tax sharing the same properties"""
        self.ensure_one()
        return str(invoice_tax_val['tax_id']) + '-' + \
               str(invoice_tax_val['account_analytic_id']) + '-' + \
               str(invoice_tax_val.get('analytic_tag_ids', []))

class PurchaseOrdersLines(models.Model):
    _inherit = 'purchase.order.line'
    taxes_id = fields.Many2many('account.tax', string='Taxes', required = True, domain=['|', ('active', '=', False), ('active', '=', True)])




    @api.one
    @api.depends('price_unit', 'taxes_id', 'product_qty',
                 'product_id', 'purchase_id.partner_id', 'purchase_id.currency_id', 'purchase_id.company_id',
                  'purchase_id.date')
    def _compute_price(self):
        currency = self.purchase_id and self.purchase_id.currency_id or None
        price = self.price_unit #* (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.taxes_id:
            taxes = self.taxes_id.compute_all(price, currency, self.product_qty, product=self.product_id,
                                                          partner=self.purchase_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.product_qty * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.purchase_id.currency_id and self.purchase_id.currency_id != self.purchase_id.company_id.currency_id:
            currency = self.purchase_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.purchase_id.company_id.currency_id,
                                                      self.company_id or self.env.user.company_id,
                                                      date or fields.Date.today())
        sign = self.purchase_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

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
    #
    # @api.depends('taxes_id')#order_line.
    # @api.multi
    # def comp_taxes(self):
    #     taxes_ids = self.env['account.tax'].search([('id','in',self.taxes_id)])#('buy_pull_id', '=', False)
    #     for tax in self.taxes_id:
    #         obj=self.env['account.invoice.tax'].create({
    #             'name': tax.name,
    #             'account_id': tax.account_id.id,
    #             'purchase_id': self.id
    #         })
    #         print(obj,'llllllllllllllllllllln')

# class AccountInvoiceInheriting(models.Model):
#     _name = 'account.invoice.purchase'
#     _inherit = 'account.invoice'


# class AccountInvoiceLineInherit(models.Model):
#     _name = 'account.purchase.lines'
#     _inherit = 'account.invoice.line'


# class AccountInvoiceTaxInherit(models.Model):
#     _name = 'account.purchase.taxes'
#     _inherit = 'account.invoice.tax'



# class AccountInvoiceTaxInherits(models.Model):
#     _inherit = 'account.invoice.tax'
#
#     @api.depends('purchase_id.order_line')
#     def _compute_base_amount(self):
#         res = super(AccountInvoiceTaxInherits, self)._compute_base_amount()
#         tax_grouped = {}
#         for purchase in self.mapped('purchase_id'):
#             tax_grouped[purchase.id] = purchase.get_taxes_values()
#         for tax in self:
#             tax.base = 0.0
#             if tax.tax_id:
#                 key = tax.tax_id.get_grouping_key({
#                     'tax_id': tax.tax_id.id,
#                     'account_id': tax.account_id.id,
#                     'account_analytic_id': tax.account_analytic_id.id,
#                     'analytic_tag_ids': tax.analytic_tag_ids.ids or False,
#                 })
#                 if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
#                     tax.base = tax_grouped[tax.invoice_id.id][key]['base']
#                 else:
#                     _logger.warning(
#                         'Tax Base Amount not computable probably due to a change in an underlying tax (%s).',
#                         tax.tax_id.name)






class AccountInvoiceTaxLine(models.Model):
    _inherit = "account.invoice"



    tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines', oldname='tax_line',
        readonly=False, states={'draft' : [('readonly', False)] ,'open': [('readonly', True)], 'paid': [('readonly', True)]}, copy=True)


class InvoiceTaxLine(models.Model):
    _inherit = "account.invoice.tax"

    amount_total = fields.Monetary(string="Amount Total", compute= '_compute_amount_total')
    change_amount = fields.Float(string="Change Amount Total", default=0)


    @api.depends('amount', 'amount_rounding', 'change_amount')
    def _compute_amount_total(self):

        for rec in self:
            for tax_line in rec:
                if rec.change_amount:
                    tax_line.amount_total = rec.change_amount
                else:
                    tax_line.amount_total = tax_line.amount + tax_line.amount_rounding
