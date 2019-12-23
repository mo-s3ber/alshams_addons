# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ChangeDigitsFloat(models.Model):
    _inherit = 'purchase.order.line'
    # price_unit = fields.Float(digits=(12, 3))
    inventory_cost = fields.Float(digits=(12, 3))
    # price_subtotal = fields.Float(digits=(12, 3))


class ChangeDigitsFloatUnitInvCost(models.Model):
    _inherit = 'stock.move'
    unit_inventory_cost = fields.Float(digits=(12, 3))


class ChangeDigitsFloatPaymentAmount(models.Model):
    _inherit = 'letter.guarantee.deduction'
    amount_total = fields.Float(digits=(12, 3))
