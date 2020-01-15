# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_deposit_offsetting_account = fields.Selection(
        related='company_id.check_deposit_offsetting_account',readonly=False)
    check_deposit_transfer_account_id = fields.Many2one(
        related='company_id.check_deposit_transfer_account_id',readonly=False)
