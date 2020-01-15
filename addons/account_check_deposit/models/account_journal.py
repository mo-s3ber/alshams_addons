# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_check = fields.Boolean(string='Check', default=False)
    credit_check_account_id = fields.Many2one('account.account', string='Check Credit Account')
    debit_check_account_id = fields.Many2one('account.account', string='Check Debit Account')

    @api.multi
    @api.onchange('credit_check_account_id')
    def onchange_credit_check_account_id(self):
        for account in self:
            if account.credit_check_account_id:
                account.debit_check_account_id = account.credit_check_account_id

    @api.multi
    @api.onchange('is_check')
    @api.constrains('is_check')
    def onchange_is_check(self):
        for line in self:
            if line.is_check == False:
                line.credit_check_account_id = False
                line.debit_check_account_id = False
