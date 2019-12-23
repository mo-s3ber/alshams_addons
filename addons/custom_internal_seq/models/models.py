# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    tax_department = fields.Char()
    tax_file = fields.Char()
    national_id = fields.Char(string='National Number')


