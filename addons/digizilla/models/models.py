# -*- coding: utf-8 -*-

from odoo import models, fields, api

class digizilla(models.Model):
    _inherit = 'sale.order'
    is_sale_order = fields.Boolean(string='Is sale order')
    partner = fields.Many2one('res.users', string='Partner',)

