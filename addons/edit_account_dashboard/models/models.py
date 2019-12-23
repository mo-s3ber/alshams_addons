# -*- coding: utf-8 -*-

from odoo import _, models, fields, api
from odoo.tools.misc import formatLang


class edit_account_dashboard(models.Model):
    # _name = 'new_module.new_module'
    _inherit = 'account.journal'

    @api.multi
    def get_journal_dashboard_datas(self):
        currency = self.currency_id or self.company_id.currency_id
        number_to_reconcile = last_balance = account_sum = 0
        title = ''
        number_draft = number_waiting = number_late = 0
        sum_draft = sum_waiting = sum_late = 0.0
        if self.type in ['bank', 'cash']:
            last_bank_stmt = self.env['account.bank.statement'].search([('journal_id', 'in', self.ids)],
                                                                       order="date desc, id desc", limit=1)
            last_balance = last_bank_stmt and last_bank_stmt[0].balance_end or 0
            # Get the number of items to reconcile for that bank journal
            self.env.cr.execute("""SELECT COUNT(DISTINCT(line.id))
                                FROM account_bank_statement_line AS line
                                LEFT JOIN account_bank_statement AS st
                                ON line.statement_id = st.id
                                WHERE st.journal_id IN %s AND st.state = 'open' AND line.amount != 0.0 AND line.account_id IS NULL
                                AND not exists (select 1 from account_move_line aml where aml.statement_line_id = line.id)
                            """, (tuple(self.ids),))
            number_to_reconcile = self.env.cr.fetchone()[0]
            # optimization to read sum of balance from account_move_line
            account_ids = tuple(
                ac for ac in [self.default_debit_account_id.id, self.default_credit_account_id.id] if ac)
            if account_ids:
                amount_field = 'aml.balance' if (
                        not self.currency_id or self.currency_id == self.company_id.currency_id) else 'aml.amount_currency'
                query = """SELECT sum(%s) FROM account_move_line aml
                               LEFT JOIN account_move move ON aml.move_id = move.id
                               WHERE aml.account_id in %%s
                               AND move.date <= %%s AND move.state = 'posted'
                               AND move.journal_id = %%s;""" % (amount_field,)
                self.env.cr.execute(query, (account_ids, fields.Date.today(), self.id))
                query_results = self.env.cr.dictfetchall()
                if query_results and query_results[0].get('sum') != None:
                    account_sum = query_results[0].get('sum')
        # TODO need to check if all invoices are in the same currency than the journal!!!!
        elif self.type in ['sale', 'purchase']:
            title = _('Bills to pay') if self.type == 'purchase' else _('Invoices owed to you')

            (query, query_args) = self._get_open_bills_to_pay_query()
            self.env.cr.execute(query, query_args)
            query_results_to_pay = self.env.cr.dictfetchall()

            (query, query_args) = self._get_draft_bills_query()
            self.env.cr.execute(query, query_args)
            query_results_drafts = self.env.cr.dictfetchall()

            today = fields.Date.today()
            query = """SELECT residual_signed as amount_total, currency_id AS currency, type, date_invoice, company_id FROM account_invoice WHERE journal_id = %s AND date <= %s AND state = 'open';"""
            self.env.cr.execute(query, (self.id, today))
            late_query_results = self.env.cr.dictfetchall()
            curr_cache = {}
            (number_waiting, sum_waiting) = self._count_results_and_sum_amounts(query_results_to_pay, currency,
                                                                                curr_cache=curr_cache)
            (number_draft, sum_draft) = self._count_results_and_sum_amounts(query_results_drafts, currency,
                                                                            curr_cache=curr_cache)
            (number_late, sum_late) = self._count_results_and_sum_amounts(late_query_results, currency,
                                                                          curr_cache=curr_cache)

        difference = currency.round(last_balance - account_sum) + 0.0
        return {
            'number_to_reconcile': number_to_reconcile,
            'account_balance': formatLang(self.env, currency.round(account_sum) + 0.0, currency_obj=currency),
            'last_balance': formatLang(self.env, currency.round(last_balance) + 0.0, currency_obj=currency),
            'difference': formatLang(self.env, difference, currency_obj=currency) if difference else False,
            'number_draft': number_draft,
            'number_waiting': number_waiting,
            'number_late': number_late,
            'sum_draft': formatLang(self.env, currency.round(sum_draft) + 0.0, currency_obj=currency),
            'sum_waiting': formatLang(self.env, currency.round(sum_waiting) + 0.0, currency_obj=currency),
            'sum_late': formatLang(self.env, currency.round(sum_late) + 0.0, currency_obj=currency),
            'currency_id': currency.id,
            'bank_statements_source': self.bank_statements_source,
            'title': title,
        }
