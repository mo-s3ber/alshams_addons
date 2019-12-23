# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AddChatter(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']
