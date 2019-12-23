# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = 'product.product'

    inventory_valuation_value = fields.Float(string="Value", compute='_compute_inventory_valuation_value', )

    @api.multi
    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state', 'stock_move_ids.remaining_value',
                 'product_tmpl_id.cost_method', 'product_tmpl_id.standard_price', 'product_tmpl_id.property_valuation',
                 'product_tmpl_id.categ_id.property_valuation')
    def _compute_inventory_valuation_value(self):
        for product in self:
            stock_journal = product.categ_id.property_stock_journal.id
            account_id = product.categ_id.property_stock_valuation_account_id.id
            domain = [('product_id', '=', product.id), ('journal_id', '=', stock_journal),
                      ('account_id', '=', account_id)]
            balances = self.env['account.move.line'].search(domain).mapped('balance')
            product.inventory_valuation_value = sum(balances)
