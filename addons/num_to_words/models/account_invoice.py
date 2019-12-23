# -*- coding: utf-8 -*-

from num2words import num2words
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.bank.statement.line"

    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )

    @api.depends('amount')
    def amount_to_words(self):
        if True:
            self.text_amount = num2words(abs(self.amount),
                                         lang='ar')