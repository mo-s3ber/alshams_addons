# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import datetime
import logging
from odoo import api, fields, models, tools
from datetime import date
import calendar
import datetime
import time
from dateutil.relativedelta import relativedelta

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}


class AccountCheckPayment(models.Model):
    _inherit = "account.payment"
    _description = "Account Check Payment"
    _order = 'due_date desc'

    def _default_my_date(self):
        return fields.Date.context_today(self)

    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    date_now = fields.Date(default=_default_my_date)
    due_date = fields.Date(string='Due Date')
    test_state = fields.Boolean(default=False)
    test = fields.Boolean(default=False)
    check_due_date = fields.Boolean(default=False)
    partner_bank = fields.Many2one('res.bank', string='Partner Bank')
    payment_type_check = fields.Selection([('payment', "Payment"),
                                           ('check', "Check"),
                                           ], default='payment', required=True, string='Payment Method')
    current_state = fields.Selection([('collected', "Collected"),
                                      ('not_collected', "Not Collected"),
                                      ('paid', "Paid"),
                                      ], default='not_collected', readonly=True, string='Current State',copy=False)

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    check_deposit_id = fields.Many2one(
        'account.check.deposit', string='Check Deposit', compute='_compute_check_deposit_id')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env['res.company'])

    is_current_week = fields.Boolean(compute="_check_current_month", store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),('under_collected', 'Under Collect'),('collected', 'Collected')], readonly=True, default='draft', copy=False, string="Status")

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_(
                    'There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property'].get('property_account_receivable_id', 'res.partner')
            self.destination_account_id = default_account.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].get('property_account_payable_id', 'res.partner')
            self.destination_account_id = default_account.id
        if self.payment_type == 'outbound' and self.payment_type_check == 'check' and self.journal_id.is_check == True:
            self.destination_account_id = self.journal_id.debit_check_account_id.id
        if self.payment_type == 'inbound' and self.payment_type_check == 'check' and self.journal_id.is_check == True:
            self.destination_account_id = self.journal_id.credit_check_account_id.id


    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'outbound' and self.payment_type_check == 'check' and self.journal_id.is_check == True:
            account = self.journal_id.debit_check_account_id.id
        if self.payment_type == 'inbound' and self.payment_type_check == 'check' and self.journal_id.is_check == True:
            account = self.journal_id.credit_check_account_id.id
        else:
            account = self.destination_account_id.id

        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name) - 2]

        return {
            'name': name,
            'account_id': account,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def button_journal_entries_collected(self):
        return {
            'name': "Collected Entry",
            'view_type': 'form',
            'domain': [('collected_id', '=', self.id)],
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    # def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
    #     """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
    #     """
    #     if self.payment_type == 'outbound' and self.payment_type_check == 'check':
    #         analytci_account = self.analytic_account_id.id
    #     else:
    #         analytci_account = False
    #
    #     return {
    #         'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
    #             'res.partner']._find_accounting_partner(self.partner_id).id or False,
    #         'invoice_id': invoice_id and invoice_id.id or False,
    #         'move_id': move_id,
    #         'debit': debit,
    #         'credit': credit,
    #         'analytic_account_id': analytci_account,
    #         'amount_currency': amount_currency or False,
    #         'collected_payment_id': self.id,
    #         'journal_id': self.journal_id.id,
    #     }

    @api.multi
    @api.depends('due_date', 'payment_type_check')
    def _check_current_month(self):
        for rec in self:
            if rec.payment_type_check == 'check':
                if str(rec.due_date) < (datetime.datetime.now() + relativedelta(days=7)).strftime('%Y-%m-%d'):
                    if str(rec.due_date) >= datetime.datetime.now().strftime('%Y-%m-%d'):
                        rec.is_current_week = True

    @api.multi
    def force_quotation_send(self):
        for order in self:
            email_act = order.send_mail_template()
            if email_act and email_act.get('context'):
                email_ctx = email_act['context']
                email_ctx.update(default_email_from=order.company_id.email)
                order.with_context(email_ctx).message_post_with_template(email_ctx.get('default_template_id'))
        return True

    @api.multi
    @api.depends('move_line_ids')
    def _compute_check_deposit_id(self):
        if self.move_line_ids:
            for len in self.move_line_ids:
                if len.check_deposit_id.state == 'done':
                    self.check_deposit_id = len.check_deposit_id.id
                    self.state = 'under_collected'

    def action_collected(self):
        for line in self:
            # step sale
            if not line.partner_id.property_account_receivable_id.id:
                raise UserError(_(
                    'There is no Receivable Account defined for partner.'))

            if not line.journal_id.debit_check_account_id:
                raise UserError(_(
                    'There is no Check Debit Account defined for this Journal.'))

            move_id = self.env['account.move'].create({
                'ref': str(line.name),
                'branch_id': line.branch_id.id,
                'journal_id': line.journal_id.id,
            })

            sale_move_lines = self.env['account.move.line'].with_context(check_move_validity=False)
            sale_move_lines |= sale_move_lines.create({
                'name': str(line.communication),
                'branch_id': line.branch_id.id,
                'account_id': line.journal_id.debit_check_account_id.id,
                'debit': line.amount,
                'move_id': move_id.id,
                'collected_id': self.id,
                # 'analytic_account_id': line.account_analytic_id.id,
                # 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'partner_id': line.partner_id.id,
            })
            sale_move_lines |= sale_move_lines.create({
                'name': str(line.communication),
                'account_id': line.partner_id.property_account_receivable_id.id,
                'branch_id': line.branch_id.id,
                # 'analytic_account_id': line.account_analytic_id.id,
                'credit': line.amount,
                'collected_id': self.id,
                'move_id': move_id.id,
                'partner_id': line.partner_id.id,
                # 'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
            })
            move_id.action_post()

            line.current_state = 'collected'
            line.state = 'collected'
            line.test_state = True


    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        if self.payment_type_check == 'payment':
            journal = journal or self.journal_id
            if not journal.sequence_id:
                raise UserError(_('Configuration Error !'),
                                _('The journal %s does not have a sequence, please specify one.') % journal.name)
            if not journal.sequence_id.active:
                raise UserError(_('Configuration Error !'),
                                _('The sequence of journal %s is deactivated.') % journal.name)
            name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
            return {
                'name': name,
                'date': self.payment_date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        if self.payment_type_check == 'check':
            journal = journal or self.journal_id
            if not journal.sequence_id:
                raise UserError(_('Configuration Error !'),
                                _('The journal %s does not have a sequence, please specify one.') % journal.name)
            if not journal.sequence_id.active:
                raise UserError(_('Configuration Error !'),
                                _('The sequence of journal %s is deactivated.') % journal.name)
            name = self.move_name or journal.with_context(
                ir_sequence_date=self.due_date).sequence_id.next_by_id()
            return {
                'name': name,
                'date': self.due_date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            if self.payment_type_check == 'payment':
                amount = self.currency_id.with_context(date=self.payment_date).compute(amount,
                                                                                       self.journal_id.currency_id)
                debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                    date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id,
                                                                  self.company_id.currency_id)
            else:
                amount = self.currency_id.with_context(date=self.due_date).compute(amount,
                                                                                   self.journal_id.currency_id)
                debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                    date=self.due_date)._compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    automation_field = fields.Char(string='Automatically Renew?', default='1')
