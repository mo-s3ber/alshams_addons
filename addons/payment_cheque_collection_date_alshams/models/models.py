# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class account_batch_payment(models.Model):
    _inherit = 'account.batch.payment'

    date_collection = fields.Date('Collection Date')

    @api.one
    def transfer_collect(self):
        if self.state_in == 'collect' and not self.date_collection:
            raise exceptions.Warning('Please fill collection date')
        if self.state_in == 'cheques_under_collection':
            self.create_journal_entry_collected()
            self.state_in = 'collect'
        else:
            super(account_batch_payment, self).transfer_collect()
        return True

    def create_journal_entry_collected(self):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        move = self.env['account.move'].search([('date', '=', self.date), ('ref', '=', self.cheque_number), ('journal_id', '=', self.journal_id.id),('journal_parent', '=', self.id)], limit=1)
        if self.state_in == 'cheques_under_collection':
            IrDefault = self.env['ir.default'].sudo()
            # ICPSudo = self.env['ir.config_parameter'].sudo()
            intermediate_account = IrDefault.get('account.batch.payment', 'account_id_receipt_intermediate',company_id=self.env.user.company_id.id)
            transfer_account = IrDefault.get('account.batch.payment', 'account_id_transfer_intermediate',company_id=self.env.user.company_id.id)

            # account_1 = self.env["ir.config_parameter"].sudo().get_param(
            #    'payement_cheque.transfer_account',)
            # credit = self.amount
            values = {
                'account_id': transfer_account,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': self.date_collection,
            }
            aml_obj.create(values)
            values = {
                'account_id': self.journal_id.default_debit_account_id.id,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': self.date_collection,
            }
            aml_obj.create(values)
        move.write({'date' : self.date_collection})
        move.post()

