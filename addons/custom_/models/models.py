# -*- coding: utf-8 -*-

from odoo import models, fields, api

class custom_(models.Model):
    _inherit = 'account.asset.asset'


    description = fields.Text("Description")
    code = fields.Char("Code")

    _sql_constraints = [
        ('Code', 'unique (code)', 'This code used before!')]

