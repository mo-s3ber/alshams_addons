# -*- coding: utf-8 -*-

from odoo import models, fields, api

class po_acc_tax(models.Model):
    _inherit = 'purchase.order'

    tax_id = fields.Many2many('account.tax')

    @api.onchange('tax_id','product_id','order_line','Analytic_id')
    def onch_tax(self):
        print(self.tax_id)
        if self.tax_id and self.Analytic_id:
            self.order_line.update({'taxes_id': self.tax_id})
            self.order_line.update({'account_analytic_id': self.Analytic_id})

class cont_acc_tax(models.Model):
    _inherit = 'subcontract.order'

    tax_id = fields.Many2many('account.tax')
    Analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('tax_id', 'product_id', 'order_line', 'Analytic_id')
    def onch_tax(self):
        print(self.tax_id)
        if self.tax_id and self.Analytic_id:
            self.order_line.update({'taxes_id': self.tax_id})
            self.order_line.update({'account_analytic_id': self.Analytic_id})


    # @api.onchange('product_id','order_line','Analytic_id')
    # def onch_tax(self):
    #     print(self.Analytic_id)
    #     if self.Analytic_id:
    #         self.order_line.update({'account_analytic_id': self.Analytic_id})


    # tax_id = fields.Many2many(comodel_name="account.tax", string='Taxes')
    # taxes  = fields.Many2one(comodel_name="purchase.order.line", string='Taxes')
    # taxes_id = fields.Many2one("purchase.order.line", string='Taxes',change_default=True, default = lambda self: self.env['purchase.order'].search(['tax_id']))
    # @api.onchange('product_id')
    # def _onchange_action_product_add(self):
    #     return {
    #         'order_line': {'taxes_id': self.tax_id}
    #     }
    # @api.multi
    # @api.onchange('order_line')
    # def get_teachers(self):
    #     tax = self.env['purchase.order'].search([])
    #
    #     tax_list = []
    #     for rec in self.tax_id:
    #         tax_list.append([0, 0, {
    #             'tax_id': self.tax_id,
    #         }])
    #     print('taxes_id', tax_list)
    #     self.taxes_id = [(6, 0, [tax_list])]
    #     self.write({'taxes_id': tax_list})

    # @api.onchange(tax_id)
    # def create(self, vals):
    #     project_ids = []
    #     stage_obj = self.env['purchase.order']
    #     result = super(po_acc_tax, self).create(vals)
    #     for resource in result:
    #         for source in resource.stage_ids:
    #             if source:
    #                 stage_id = stage_obj.search([('tax_id', '=', source.tax_id)])
    #                 project_ids.append(result.id)
    #                 stage_id.update({'taxes_id': [(6, 0, project_ids)]})
    #     return result
    # @api.multi
    # @api.onchange('tax_id')
    # def Create_One2many_method(self):
    #     print(self.tax_id)
        # res = []
        # res = self.env['purchase.order'].search([])
        # for record in res:
        #     record.write({ 'order_line': [(0, 0, {'taxes_id': record.tax_id.id })] })



