# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BankAnalyticAccount(models.Model):
    _inherit ='account.bank.statement'
    # _inherit ='account.bank.statement'payment_analytic_account_alshams


    def default_invo_id(self):
        context = self.env.context
        if context.get('id'):
            invoicess_id = self.env['account.invoice'].search(
                [ ('id', '=', context.get('id'))])
            return invoicess_id.analytic_id.id

    analytic_account_id = fields.Many2one('account.analytic.account', groups="analytic.group_analytic_accounting")

    @api.depends('state')
    def set_analytic_accounts(self):

        ids = self.move_line_ids._ids
        for id in ids :
            account_move_line_obj = self.env['account.move.line'].search([])



            for rec in account_move_line_obj:
                if rec._ids[0] == id:
                    print('ok')
                    rec.analytic_account_id = self.line_ids.analytic_account_id
                    # if not self.analytic_account_id.id:
                    #     self.env['account.analytic.line'].create({
                    #         'account_id': self.analytic_account_id.id,
                    #         'name': self.name,
                    #         'date': self.date,
                    #         'partner_id': self.partner_id
                    #          })




    @api.multi
    def check_confirm_bank(self):
        account_move_line_obj = self.env['account.move.line'].search([('move_id','=',self.id)])

        for rec in account_move_line_obj:
            rec.analytic_account_id = self.analytic_account_id.id
            if self.analytic_account_id.id:
               self.env['account.analytic.line'].create({
                  'account_id': self.analytic_account_id.id,
                  'name': self.name,
                  'date': self.date,
                  'partner_id': self.partner_id.id
                })


class BankAnalyticAccountLine(models.Model):
    _inherit='account.bank.statement.line'
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic account',  groups="analytic.group_analytic_accounting")

    def process_reconciliation(self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None):
        moves = super(BankAnalyticAccountLine, self).process_reconciliation(counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)
        for move in moves:
            ids = []
            for aml in move.line_ids:
                if aml.id not in ids and aml.analytic_account_id:
                    ids2 = move.line_ids.filtered(lambda r: r.partner_id.id == aml.partner_id.id and r.id != aml.id)
                    ids.append(aml.id)
                    ids.extend(ids2.ids)
                    ids2.write({
                        'analytic_account_id': aml.analytic_account_id.id
                    })
        return moves

class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def get_bank_statement_line_data(self, st_line_ids, excluded_ids=None):
        """ Returns the data required to display a reconciliation widget, for
            each statement line in self

            :param st_line_id: ids of the statement lines
            :param excluded_ids: optional move lines ids excluded from the
                result
        """
        excluded_ids = excluded_ids or []

        # Make a search to preserve the table's order.
        bank_statement_lines = self.env['account.bank.statement.line'].search([('id', 'in', st_line_ids)])
        reconcile_model = self.env['account.reconcile.model'].search([('rule_type', '!=', 'writeoff_button')])

        # Search for missing partners when opening the reconciliation widget.
        partner_map = self._get_bank_statement_line_partners(bank_statement_lines)

        matching_amls = reconcile_model._apply_rules(bank_statement_lines, excluded_ids=excluded_ids,
                                                     partner_map=partner_map)

        results = {
            'lines': [],
            'value_min': 0,
            'value_max': len(bank_statement_lines),
            'reconciled_aml_ids': [],
        }

        # Iterate on st_lines to keep the same order in the results list.
        bank_statements_left = self.env['account.bank.statement']
        for line in bank_statement_lines:
            if matching_amls[line.id].get('status') == 'reconciled':
                reconciled_move_lines = matching_amls[line.id].get('reconciled_lines')
                results['value_min'] += 1
                results['reconciled_aml_ids'] += reconciled_move_lines and reconciled_move_lines.ids or []
            else:
                aml_ids = matching_amls[line.id]['aml_ids']
                bank_statements_left += line.statement_id
                target_currency = line.currency_id or line.journal_id.currency_id or line.journal_id.company_id.currency_id

                amls = aml_ids and self.env['account.move.line'].browse(aml_ids)
                line_vals = {
                    'analytic_account_id': line.analytic_account_id.id,
                    'analytic_account_name': line.analytic_account_id.name,
                    'st_line': self._get_statement_line(line),
                    'reconciliation_proposition': aml_ids and self._prepare_move_lines(amls,
                                                                                       target_currency=target_currency,
                                                                                       target_date=line.date) or [],
                    'model_id': matching_amls[line.id].get('model') and matching_amls[line.id]['model'].id,
                    'write_off': matching_amls[line.id].get('status') == 'write_off',
                }
                if not line.partner_id and partner_map.get(line.id):
                    partner = self.env['res.partner'].browse(partner_map[line.id])
                    line_vals.update({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                    })
                results['lines'].append(line_vals)

        return results

# class account_move(models.Model):
#     _inherit='account.move'
#
#     @api.model
#     def create(self, values):
#         res = super(account_move, self).create(values)
#         for res.line_ids
#         if res.analytic_account_id:
#             line_ids = res.move_id.filtered(lambda r: r.id != res.id and r.partner_id.id == res.partner_id.id)
#             line_ids.write({'analytic_account_id': res.analytic_account_id.id})
#         return res