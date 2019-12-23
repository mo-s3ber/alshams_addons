# -*- coding: utf-8 -*-

from odoo import models, fields, api

class payment_analytic_account_alshams(models.Model):
    _inherit = 'account.payment'


    def default_invo_id(self):
        context = self.env.context
        if context.get('id'):
            invoicess_id = self.env['account.invoice'].search(
                [ ('id', '=', context.get('id'))])
            return invoicess_id.analytic_id.id

    analytic_account = fields.Many2one('account.analytic.account', default=default_invo_id)
    # tagss_id = fields.Many2one('account.analytic.tag')
    analytic_tag = fields.Many2many('account.analytic.tag','payment_tags_rel', 'tagss_id', 'paymentss_id')


    def post(self):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        # aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        # debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        #
        # move = self.env['account.move'].create(self._get_move_vals())
        #
        # #Write line corresponding to invoice payment
        # counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        # counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        # counterpart_aml_dict.update({'currency_id': currency_id})
        # counterpart_aml = aml_obj.create(counterpart_aml_dict)
        #
        # #Reconcile with the invoices
        # if self.payment_difference_handling == 'reconcile' and self.payment_difference:
        #     writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
        #     debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
        #     writeoff_line['name'] = self.writeoff_label
        #     writeoff_line['account_id'] = self.writeoff_account_id.id
        #     writeoff_line['debit'] = debit_wo
        #     writeoff_line['credit'] = credit_wo
        #     writeoff_line['amount_currency'] = amount_currency_wo
        #     writeoff_line['currency_id'] = currency_id
        #     writeoff_line = aml_obj.create(writeoff_line)
        #     if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
        #         counterpart_aml['debit'] += credit_wo - debit_wo
        #     if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
        #         counterpart_aml['credit'] += debit_wo - credit_wo
        #     counterpart_aml['amount_currency'] -= amount_currency_wo
        #
        # #Write counterpart lines
        # if not self.currency_id.is_zero(self.amount):
        #     if not self.currency_id != self.company_id.currency_id:
        #         amount_currency = 0
        #     liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        #     aml_obj.create(liquidity_aml_dict)
        #
        # #validate the payment
        # if not self.journal_id.post_at_bank_rec:
        #     move.post()
        #
        # #reconcile the invoice receivable/payable line(s) with the payment
        # if self.invoice_ids:
        #     self.invoice_ids.register_payment(counterpart_aml)
        #
        # return move
        res = super(payment_analytic_account_alshams, self).post()
        account_move_line_obj = self.env['account.move.line'].search([('payment_id','=',self.id)])
        if self.payment_type == 'outbound':
            my_name = 'Send Money'
        elif self.payment_type == 'inbound':
            my_name = 'Receive Money'
        else:
            my_name = 'Internal Transfer'
        for rec in account_move_line_obj:
            # if rec.account_id.id ==self.journal_id.default_debit_account_id.id or rec.account_id.id ==self.journal_id.default_credit_account_id.id:
            rec.analytic_account_id = self.analytic_account.id
            rec.analytic_tag_ids = self.analytic_tag.ids
            if self.analytic_account.id:
                self.env['account.analytic.line'].create({
                    'account_id': self.analytic_account.id,
                    'name' : my_name,
                    'amount' : self.amount,
                    'date' : self.payment_date,
                    'partner_id' : self.partner_id.id
                })
        print (account_move_line_obj,'Account moveeeeeeeeeeeeeeeee')


        return res


# class Customaccountanalytictag(models.Model):
#     _inherit = 'account.analytic.tag'
#
#     paymentss_id = fields.Many2one('account.payment')




