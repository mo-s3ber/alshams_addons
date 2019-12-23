# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomProgressInvoice(models.Model):
    _inherit = 'account.invoice'

    project_code = fields.Char(string='Project Code', compute='_compute_project_code')

    @api.depends('account_analytic_id.code')
    def _compute_project_code(self):
        for rec in self:
            if rec.account_analytic_id.code:
                rec.project_code = rec.account_analytic_id.code
            else:
                rec.project_code = rec.analytic_id.code

    # settlements data

    sum_total_amount = fields.Monetary(string="اجمالي الاعمال", currency_field='currency_id',
                                       compute='_compute_sum_total_amount')

    @api.depends('invoice_line_ids.total_amount')
    def _compute_sum_total_amount(self):
        for rec in self:
            tmp_total = 0

            for invoice_line in rec.invoice_line_ids:
                tmp_total += invoice_line.total_amount

            rec.sum_total_amount = tmp_total

    sum_A_T_tax = fields.Monetary(string="خصم أ.ت.ص", currency_field='currency_id',
                                  compute='_compute_sum_taxs_baseon_type')

    sum_kowa_amly_tax = fields.Monetary(string="خصم قوي عاملة", currency_field='currency_id',
                                        compute='_compute_sum_taxs_baseon_type')

    sum_tameynat_tax = fields.Monetary(string="خصم تامينات اجتماعية", currency_field='currency_id',
                                       compute='_compute_sum_taxs_baseon_type')

    sum_tameynat_mohtagz_tax = fields.Monetary(string="خصم تأمين محتجز", currency_field='currency_id',
                                               compute='_compute_sum_taxs_baseon_type')

    sum_daf3t_tax = fields.Monetary(string="خصم دفعات مقدمة", currency_field='currency_id',
                                    compute='_compute_sum_taxs_baseon_type')

    sum_tamyn_a3mal_tax = fields.Monetary(string="خصم تامين اعمال", currency_field='currency_id',
                                          compute='_compute_sum_taxs_baseon_type')

    # sum_rest_tax = fields.Monetary(string="خصومات أخري", currency_field='currency_id',
    #                                       compute='_compute_sum_taxs_baseon_type')

    sum_all_tax = fields.Monetary(string="اجمالي الاستقطاعات", currency_field='currency_id',
                                  compute='_compute_sum_taxs_baseon_type')
    net = fields.Monetary(string="صافي الاعمال", currency_field='currency_id',
                          compute='_compute_sum_taxs_baseon_type')

    @api.depends('invoice_line_ids', 'tax_line_ids')
    def _compute_sum_taxs_baseon_type(self):

        for progress_invoice_record in self:
            # total_rest_tax = 0
            total_kowa_amly = 0
            total_a_t_tax = 0
            total_tamynat_tax = 0
            total_tameynat_mohtagz_tax = 0
            total_daf3t_tax = 0
            total_tamyn_a3mal_tax = 0
            # total_all_tax = 0
            for invoice_line in progress_invoice_record.invoice_line_ids:
                for tax_line in invoice_line.invoice_line_tax_ids:
                    tax_type = tax_line.tax_type
                    tax_for_total_amount = (tax_line.amount / 100) * invoice_line.total_amount
                    if tax_type == 'قوي عاملة':
                        total_kowa_amly += tax_for_total_amount
                    elif tax_type == 'أ.ت.ص':
                        total_a_t_tax += tax_for_total_amount
                    elif tax_type == 'تامينات اجتماعية':
                        total_tamynat_tax += tax_for_total_amount
                    elif tax_type == 'تأمين محتجز':
                        total_tameynat_mohtagz_tax += tax_for_total_amount
                    elif tax_type == 'دفعات مقدمة':
                        total_daf3t_tax += tax_for_total_amount
                    elif tax_type == 'تامين اعمال':
                        total_tamyn_a3mal_tax += tax_for_total_amount
                    # else:
                    #     total_rest_tax += tax_for_total_amount

            total_all_tax = total_a_t_tax + total_tamyn_a3mal_tax + total_tameynat_mohtagz_tax
            total_all_tax += total_kowa_amly + total_daf3t_tax + total_tamynat_tax

            progress_invoice_record.sum_A_T_tax = total_a_t_tax * -1
            progress_invoice_record.sum_kowa_amly_tax = total_kowa_amly * -1
            progress_invoice_record.sum_daf3t_tax = total_daf3t_tax * -1
            progress_invoice_record.sum_tameynat_tax = total_tamynat_tax * -1
            progress_invoice_record.sum_tameynat_mohtagz_tax = total_tameynat_mohtagz_tax * -1
            progress_invoice_record.sum_tamyn_a3mal_tax = total_tamyn_a3mal_tax * -1
            progress_invoice_record.sum_all_tax = total_all_tax * -1
            # progress_invoice_record.sum_rest_tax = total_rest_tax * -1
            progress_invoice_record.net = progress_invoice_record.sum_total_amount + total_all_tax

    sum_payments = fields.Monetary(string="دفعات", currency_field='currency_id',
                                   compute='_compute_debit_payments')

    @api.depends('invoice_line_ids', 'partner_id', 'account_analytic_id')
    def _compute_debit_payments(self):
        company = self.env.user.company_id
        account_id = company.payments.id
        progress_invoice_journal_id = self.get_progress_invoice_journal_id()
        for rec in self:
            domain = [
                # ('journal_id.id', '=', progress_invoice_journal_id),
                ('partner_id', '=', rec.partner_id.id),
                ('account_id.id', '=', account_id),
                ('analytic_account_id', '=', rec.account_analytic_id.id)]
            if rec.journal_id.id != progress_invoice_journal_id:
                domain = [
                    ('journal_id.name', 'not ilike', '%progress%%'),
                    # ('partner_id', '=', rec.partner_id.id),
                    ('analytic_account_id', '=', rec.analytic_id.id),
                    ('account_id.id', '=', account_id)]

            account_move_lines = rec.env['account.move.line'].search(domain)
            total_payments = 0
            for line in account_move_lines:
                total_payments += line.debit

            rec.sum_payments = total_payments

    balance_Balance_due = fields.Monetary(string="رصيد مستحق", currency_field='currency_id',
                                          compute='_compute_balance_Balance_due')

    @api.depends('invoice_line_ids', 'partner_id', 'account_analytic_id')
    def _compute_balance_Balance_due(self):
        company = self.env.user.company_id
        account_id = company.Balance_due.id
        progress_invoice_journal_id = self.get_progress_invoice_journal_id()
        for rec in self:
            domain = [
                # ('journal_id.id', '=', progress_invoice_journal_id),
                ('partner_id', '=', rec.partner_id.id),
                ('analytic_account_id', '=', rec.account_analytic_id.id),
                ('account_id.id', '=', account_id)]
            if rec.journal_id.id != progress_invoice_journal_id:
                domain = [
                    ('journal_id.name', 'not ilike', '%progress%%'),
                    ('partner_id', '=', rec.partner_id.id),
                    ('analytic_account_id', '=', rec.analytic_id.id),
                    ('account_id.id', '=', account_id)]

            account_move_lines = rec.env['account.move.line'].search(domain)
            total_balance = 0
            for line in account_move_lines:
                total_balance += line.balance

            rec.balance_Balance_due = total_balance

    balance_advance_payment = fields.Monetary(string="رصيد دفعة مقدمة ", currency_field='currency_id',
                                              compute='_compute_balance_advance_payment')

    @api.depends('invoice_line_ids', 'partner_id', 'account_analytic_id')
    def _compute_balance_advance_payment(self):
        company = self.env.user.company_id
        account_id = company.advance_payment.id
        progress_invoice_journal_id = self.get_progress_invoice_journal_id()
        for rec in self:
            domain = [
                # ('journal_id.id', '=', progress_invoice_journal_id),
                ('partner_id', '=', rec.partner_id.id),
                ('analytic_account_id', '=', rec.account_analytic_id.id),
                ('account_id.id', '=', account_id)]

            if rec.journal_id.id != progress_invoice_journal_id:
                domain = [
                    ('journal_id.name', 'not ilike', '%progress%%'),
                    ('partner_id', '=', rec.partner_id.id),
                    ('analytic_account_id', '=', rec.analytic_id.id),
                    ('account_id.id', '=', account_id)]

            account_move_lines = rec.env['account.move.line'].search(domain)
            total_balance = 0
            for line in account_move_lines:
                total_balance += line.balance

            rec.balance_advance_payment = total_balance

    balance_reserved_insurance = fields.Monetary(string="رصيد التامين المحجوز", currency_field='currency_id',
                                                 compute='_compute_balance_reserved_insurance')

    @api.depends('invoice_line_ids', 'partner_id', 'account_analytic_id')
    def _compute_balance_reserved_insurance(self):
        company = self.env.user.company_id
        account_id = company.reserved_insurance.id
        progress_invoice_journal_id = self.get_progress_invoice_journal_id()
        for rec in self:

            domain = [
                # ('journal_id.id', '=', progress_invoice_journal_id),
                ('partner_id', '=', rec.partner_id.id),
                ('analytic_account_id', '=', rec.account_analytic_id.id),
                ('account_id.id', '=', account_id)]
            if rec.journal_id.id != progress_invoice_journal_id:
                domain = [
                    ('journal_id.name', 'not ilike', '%progress%%'),
                    ('partner_id', '=', rec.partner_id.id),
                    ('analytic_account_id', '=', rec.analytic_id.id),
                    ('account_id.id', '=', account_id)]

            account_move_lines = rec.env['account.move.line'].search(domain)
            total_balance = 0
            for line in account_move_lines:
                total_balance += line.balance

            rec.balance_reserved_insurance = total_balance

    def get_progress_invoice_journal_id(self):
        # progress_invoice_journal = self.env['account.journal'].search([('name', '=', 'Progress Invoice')])
        progress_invoice_journal = self.env['account.journal'].search([('name', 'ilike', '%progress%%')])
        return progress_invoice_journal.id
