# -*- coding: utf-8 -*-

import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import date


class SaleOrderReport(models.TransientModel):
    _name = "progressinvoice.report"

    start_date = fields.Date(string='Start Date', required=True, default=date.today().replace(day=1))
    end_date = fields.Date(string="End Date", required=True, default=date.today().replace(
        day=calendar.monthrange(date.today().year, date.today().month)[1]))
    order_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, required=True)
    progress_invoice_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Financial Procurement Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    _sql_constraints = [
        ('check', 'CHECK((start_date <= end_date))', "End date must be greater then start date")
    ]

    @api.multi
    def action_progress_invoice_report(self):
        progress_invoice_journal = self.env['account.journal'].search([('name', '=', 'Progress Invoice')])

        x_domain = [('journal_id.id', '=', progress_invoice_journal.id), ('state', '=', 'open'), ]
        _fields = ['name']
        subcontract_requisition_groups = self.env['account.invoice'].read_group(fields=_fields,
                                                                                groupby='subcontract_requisition_id',
                                                                                domain=x_domain)
        workbook = xlwt.Workbook(encoding="UTF-8")
        style_text_align_vert_center_horiz_center = xlwt.easyxf("align: vert centre, horiz centre")

        sheet = workbook.add_sheet("Financial Procurement Report")
        sheet.cols_right_to_left = True
        cols = 20
        for col_index in range(cols):
            sheet.col(col_index).width = int(20 * 260)
        # المشروع
        sheet.col(3).width = int(50 * 260)
        # المقاول
        sheet.col(4).width = int(50 * 260)

        sheet.write(0, 0, 'رقم المستخلص', style_text_align_vert_center_horiz_center)
        sheet.write(0, 1, 'تاريخ المستخلص', style_text_align_vert_center_horiz_center)
        sheet.write(0, 2, 'رقم المشروع', style_text_align_vert_center_horiz_center)
        sheet.write(0, 3, 'المشروع', style_text_align_vert_center_horiz_center)
        sheet.write(0, 4, 'المقاول', style_text_align_vert_center_horiz_center)
        sheet.write(0, 5, 'طبيعه العمل ', style_text_align_vert_center_horiz_center)
        sheet.write(0, 6, 'إجمالي الأعمال', style_text_align_vert_center_horiz_center)
        sheet.write(0, 7, 'خصم أ.ت.ص.', style_text_align_vert_center_horiz_center)
        sheet.write(0, 8, 'خصم قوى عاملة', style_text_align_vert_center_horiz_center)
        sheet.write(0, 9, 'خصم دفعات مقدمة', style_text_align_vert_center_horiz_center)
        sheet.write(0, 10, 'تامينات اجتماعية', style_text_align_vert_center_horiz_center)
        sheet.write(0, 11, 'رصيد تأمين محتجز', style_text_align_vert_center_horiz_center)
        sheet.write(0, 12, 'اجمالي الاستقطاعات', style_text_align_vert_center_horiz_center)
        sheet.write(0, 13, 'صافى الأعمال', style_text_align_vert_center_horiz_center)
        sheet.write(0, 14, 'الدفعات', style_text_align_vert_center_horiz_center)
        sheet.write(0, 15, 'رصيد دفعة مقدمة', style_text_align_vert_center_horiz_center)
        sheet.write(0, 16, 'رصيد التامين المحجوز', style_text_align_vert_center_horiz_center)
        sheet.write(0, 17, 'رصيد مستحق', style_text_align_vert_center_horiz_center)
        sheet.write(0, 18, 'خصومات أخرى', style_text_align_vert_center_horiz_center)
        sheet.write(0, 19, 'المطلوب سداده', style_text_align_vert_center_horiz_center)
        sheet.write(0, 20, 'المتاح', style_text_align_vert_center_horiz_center)
        sheet.write(0, 21, 'ملاحظات', style_text_align_vert_center_horiz_center)

        progress_invoice_partner_analytic_account = dict()

        for index, subcontract_requisition in enumerate(subcontract_requisition_groups):
            subcontract_requisition_id = subcontract_requisition.get('subcontract_requisition_id', -1)[0]
            x_domain = [('journal_id.id', '=', progress_invoice_journal.id), ('state', '=', 'open'),
                        ('subcontract_requisition_id.id', '=', subcontract_requisition_id)]

            rec = self.env['account.invoice'].search(x_domain, limit=1)

            partner_analytic_account_key = str(rec.account_analytic_id.id) + str(rec.partner_id.id)

            progress_invoice_partner_analytic_account[partner_analytic_account_key] = True

            sheet.write(index + 1, 0, rec.display_name if rec.display_name else '')
            sheet.write(index + 1, 1, str(rec.date_invoice) if rec.date_invoice else '')
            sheet.write(index + 1, 2, rec.project_code if rec.project_code else '')
            sheet.write(index + 1, 3,
                        rec.account_analytic_id.display_name if rec.account_analytic_id.display_name else '')
            sheet.write(index + 1, 4, rec.partner_id.name if rec.partner_id.name else '')
            sheet.write(index + 1, 5,
                        rec.subcontract_requisition_id.category_id.display_name if rec.subcontract_requisition_id.category_id.display_name else '')
            sheet.write(index + 1, 6, round(rec.sum_total_amount, 2) if rec.sum_total_amount else '')
            sheet.write(index + 1, 7, round(rec.sum_A_T_tax, 2) if rec.sum_A_T_tax else '')
            sheet.write(index + 1, 8, round(rec.sum_kowa_amly_tax, 2) if rec.sum_kowa_amly_tax else '')
            sheet.write(index + 1, 9, round(rec.sum_daf3t_tax, 2) if rec.sum_daf3t_tax else '')
            sheet.write(index + 1, 10, round(rec.sum_tameynat_tax, 2) if rec.sum_tameynat_tax else '')
            sheet.write(index + 1, 11, round(rec.sum_tameynat_mohtagz_tax, 2) if rec.sum_tameynat_mohtagz_tax else '')
            sheet.write(index + 1, 12, round(rec.sum_all_tax, 2) if rec.sum_all_tax else '')
            sheet.write(index + 1, 13, round(rec.net, 2) if rec.net else '')
            sheet.write(index + 1, 14, round(rec.sum_payments, 2) if rec.sum_payments else '')
            sheet.write(index + 1, 15, round(rec.balance_advance_payment, 2) if rec.balance_advance_payment else '')
            sheet.write(index + 1, 16,
                        round(rec.balance_reserved_insurance, 2) if rec.balance_reserved_insurance else '')
            sheet.write(index + 1, 17, round(rec.balance_Balance_due, 2) if rec.balance_Balance_due else '')

        tuple_of_progress = tuple(progress_invoice_partner_analytic_account.keys())

        margin = len(subcontract_requisition_groups) + 1
        company = self.env.user.company_id
        payments_account = company.payments
        balance_due_account = company.Balance_due
        advance_payment_account = company.advance_payment
        reserved_insurance_account = company.reserved_insurance

        payments_code = payments_account.code
        balance_due_code = balance_due_account.code
        advance_payment_code = advance_payment_account.code
        reserved_insurance_code = reserved_insurance_account.code
        codes = [payments_code, balance_due_code, advance_payment_code, reserved_insurance_code]

        x_domain = [('account_id.code', 'in', codes)]
        partner_groups = self.env['account.move.line'].read_group(fields=['name'], groupby=['partner_id'],
                                                                  domain=x_domain)

        index = 0
        for partner_group in partner_groups:
            analytic_account_groups = self.env['account.move.line'].read_group(fields=['name'],
                                                                               groupby=['analytic_account_id'],
                                                                               domain=partner_group['__domain'])
            for analytic_account_group in analytic_account_groups:
                lines = self.env['account.move.line'].search(analytic_account_group['__domain'])
                debit_payments = 0
                balance_advance_payment = 0
                balance_Balance_due = 0
                balance_reserved_insurance = 0

                for line in lines:
                    if line.account_id.code == payments_code:
                        debit_payments += line.debit
                    if line.account_id.code == balance_due_code:
                        balance_Balance_due += line.balance
                    if line.account_id.code == advance_payment_code:
                        balance_advance_payment += line.balance
                    if line.account_id.code == reserved_insurance_code:
                        balance_reserved_insurance += line.balance

                partner_analytic_account_key = str(lines[0].analytic_account_id.id) + str(lines[0].partner_id.id)

                if partner_analytic_account_key not in tuple_of_progress:
                    sheet.write(index + margin, 3, lines[0].analytic_account_id.display_name if lines[
                        0].analytic_account_id.display_name else '')
                    sheet.write(index + margin, 4, lines[0].partner_id.name if lines[0].partner_id.name else '')
                    sheet.write(index + margin, 14, round(debit_payments, 2) if debit_payments else '')
                    sheet.write(index + margin, 15,
                                round(balance_advance_payment, 2) if balance_advance_payment else '')
                    sheet.write(index + margin, 16,
                                round(balance_reserved_insurance, 2) if balance_reserved_insurance else '')
                    sheet.write(index + margin, 17,
                                round(balance_Balance_due, 2) if balance_Balance_due else '')
                    index += 1

        fp = StringIO()
        file_name = '/tmp/Financial Procurement Report.xls'
        workbook.save(file_name)
        file = open(file_name, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        self.write(
            {'state': 'get', 'file_name': out, 'progress_invoice_data': 'Financial Procurement Report.xls'})

        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'progressinvoice.report',
            'name': 'Financial Procurement Report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }
