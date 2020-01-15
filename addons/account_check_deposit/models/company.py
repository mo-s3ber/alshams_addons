# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    check_deposit_offsetting_account = fields.Selection([
        ('bank_account', 'Bank Account'),
        ('transfer_account', 'Transfer Account'),
        ], string='Check Deposit Offsetting Account', default='bank_account')
    check_deposit_transfer_account_id = fields.Many2one(
        'account.account', string='Transfer Account for Check Deposits',
        ondelete='restrict', copy=False,
        domain=[('reconcile', '=', True), ('deprecated', '=', False)])
