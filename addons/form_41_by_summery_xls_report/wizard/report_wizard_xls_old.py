# -*- coding: utf-8 -*-

import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from datetime import date


def report_header(workbook, sheet):
    xlwt.add_palette_colour("f2f2f2", 0x8)
    workbook.set_colour_RGB(0x8, 242, 242, 242)
    style_string_f2f2f2 = "font: bold on, height 240;\
            borders: top_color f2f2f2, bottom_color f2f2f2, right_color f2f2f2, left_color f2f2f2,\
            left thin, right thin, top thin, bottom thin;\
            pattern: pattern solid, fore_colour f2f2f2;"
    style_f2f2f2 = xlwt.easyxf(style_string_f2f2f2)

    xlwt.add_palette_colour("a2a2a2", 0x9)
    workbook.set_colour_RGB(0x9, 162, 162, 162)

    style_string_a2a2a2 = "font: bold on, height 240;\
                    borders: top_color a2a2a2, bottom_color a2a2a2, right_color a2a2a2, left_color a2a2a2,\
                    left thin, right thin, top thin, bottom thin;\
                    pattern: pattern solid, fore_colour a2a2a2;\
                    align: vert centre, horiz centre;"
    style_a2a2a2 = xlwt.easyxf(style_string_a2a2a2)

    xlwt.add_palette_colour("white", 0x10)
    workbook.set_colour_RGB(0x10, 255, 255, 255)
    style_string_white = "font: bold on;\
                            borders: top_color white, right_color white, left_color white,\
                            left thin, right thin, top thin, bottom thin;\
                            pattern: pattern solid, fore_colour white;\
                            align: vert centre, horiz centre;"
    style_white = xlwt.easyxf(style_string_white)
    cols = 16
    for col_index in range(cols):
        sheet.write(0, col_index, '', style=style_f2f2f2)
        sheet.write(3, col_index, '', style=style_f2f2f2)
        sheet.write(5, col_index, '', style=style_f2f2f2)
        sheet.write(7, col_index, '', style=style_f2f2f2)
        sheet.write(11, col_index, '', style=style_f2f2f2)
        sheet.write(13, col_index, '', style=style_f2f2f2)
        sheet.write(15, col_index, '', style=style_f2f2f2)
        sheet.write(16, col_index, '', style=style_a2a2a2)
        sheet.write(18, col_index, '', style=style_a2a2a2)
        sheet.write(19, col_index, '', style=style_white)
        if col_index == 1:
            sheet.write(1, col_index, 'وزارة المالية', style=style_a2a2a2)
            sheet.write(2, col_index, 'مصلحة الضرائب العامة', style=style_a2a2a2)
            sheet.write_merge(4, 4, col_index, col_index + 1, 'رقـــم المســـتند', style=style_f2f2f2)
            sheet.write_merge(6, 6, col_index, col_index + 1, 'رقـــم الجـهــــة', style=style_f2f2f2)
            sheet.write_merge(8, 8, col_index, col_index + 1, 'إســم الجهــــــة', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write_merge(10, 10, col_index, col_index + 1, 'عـنـوان الجهـة', style=style_f2f2f2)
            sheet.write_merge(12, 12, col_index, col_index + 1, 'كود نـوع الجهة', style=style_f2f2f2)
            sheet.write_merge(14, 14, col_index, col_index + 3,
                              '( عام -خاص- أعمال - حكومة - نقابة - نادى - فرع أجنبى - هيئة عامة )',
                              style=style_f2f2f2)
            sheet.write_merge(17, 17, col_index, col_index + 3, 'بيان المحصل تحت حساب الضريبة عن المدة',
                              style=style_a2a2a2)
        elif col_index == 2:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
        elif col_index == 3:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write_merge(4, 4, col_index, col_index + 1, '')
            sheet.write_merge(6, 6, col_index, col_index + 1, '')
            sheet.write_merge(8, 8, col_index, col_index + 1, '')
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write_merge(10, 10, col_index, col_index + 1, '')
            sheet.write(12, col_index, 'خاص')
        elif col_index == 4:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(9, col_index, '', style=style_f2f2f2)

            sheet.write(12, col_index, 'تليفون الجهة', style=style_f2f2f2)
        elif col_index == 5:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write_merge(6, 6, col_index, col_index + 1, 'مرفق مع هذا شيك رقم', style=style_f2f2f2)
            sheet.write(8, col_index, 'فقط وقدره', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, 'بتاريخ', style=style_f2f2f2)
            sheet.write_merge(12, 12, col_index, col_index + 1, '')
            sheet.write(14, col_index, 'خاص')
            sheet.write(17, col_index, '', style=style_a2a2a2)
        elif col_index == 6:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            # sheet.write(6, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(14, col_index, '', style=style_f2f2f2)
            sheet.write(17, col_index, '', style=style_a2a2a2)
        elif col_index == 7:
            sheet.write(1, col_index, 'نموذج رقم ( 41 ) خصم وإضافة وتحصيل', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index,
                        'السيد الأستاذ مدير عام الإدارة العامة لتجميع نماذج الخصم والتحصيل تحت حساب الضريبة بالقاهرة',
                        style=style_f2f2f2)
            sheet.write_merge(6, 6, col_index, col_index + 1, '')
            sheet.write_merge(8, 8, col_index, col_index + 1, '')
            sheet.write(9, col_index, 'يوم', style=style_f2f2f2)
            sheet.write_merge(10, 10, col_index, col_index + 1, '')
            sheet.write(12, col_index, '', style=style_f2f2f2)
            sheet.write_merge(14, 14, col_index, col_index + 3,
                              'قيمة المبالغ المحصلة من الممولين طبقا للنموذج / والنماذج المرفقة وعددها',
                              style=style_f2f2f2)
            sheet.write_merge(17, 17, col_index, col_index + 3, '(الأولى/ الثانية / الثالثة / الرابعة )',
                              style=style_a2a2a2)
        elif col_index == 8:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, 'شهر                    سنه', style=style_f2f2f2)
            sheet.write_merge(12, 12, col_index, col_index + 1, 'المسحوب على بنك', style=style_f2f2f2)
        elif col_index == 9:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write_merge(6, 6, col_index, col_index + 1, 'بمبلغ', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
        elif col_index == 10:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
        elif col_index == 11:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(12, col_index, '', style=style_f2f2f2)
            sheet.write(14, col_index, '', style=style_f2f2f2)
            sheet.write(17, col_index, '', style=style_a2a2a2)
        elif col_index == 12:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(12, col_index, '', style=style_f2f2f2)
            sheet.write(14, col_index, '', style=style_f2f2f2)
            sheet.write(17, col_index, '', style=style_a2a2a2)
        elif col_index == 13:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(12, col_index, 'فرع', style=style_f2f2f2)
            sheet.write(17, col_index, 'لسنة', style=style_a2a2a2)
        elif col_index == 14:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(14, col_index, 'نموذج', style=style_f2f2f2)
        else:
            sheet.write(1, col_index, '', style=style_a2a2a2)
            sheet.write(2, col_index, '', style=style_a2a2a2)
            sheet.write(4, col_index, '', style=style_f2f2f2)
            sheet.write(6, col_index, '', style=style_f2f2f2)
            sheet.write(8, col_index, '', style=style_f2f2f2)
            sheet.write(9, col_index, '', style=style_f2f2f2)
            sheet.write(10, col_index, '', style=style_f2f2f2)
            sheet.write(12, col_index, '', style=style_f2f2f2)
            sheet.write(14, col_index, '', style=style_f2f2f2)
            sheet.write(17, col_index, '', style=style_a2a2a2)

    xlwt.add_palette_colour("black", 0x11)
    workbook.set_colour_RGB(0x11, 0, 0, 0)
    style_string_a2a2a2 = "font: bold on;\
                            borders: top_color black, bottom_color black, right_color black, left_color black,\
                            left thin, right thin, top thin, bottom thin;\
                            pattern: pattern solid, fore_colour a2a2a2;\
                            align: vert centre, horiz centre;alignment: wrap on;"
    style_a2a2a2 = xlwt.easyxf(style_string_a2a2a2)

    sheet.col(0).width = 1000
    sheet.write_merge(20, 21, 0, 0, 'م', style=style_a2a2a2)
    sheet.write_merge(20, 21, 1, 1, 'رقم التسجيل الضريبى', style=style_a2a2a2)
    sheet.write_merge(20, 21, 2, 2, 'رقم الملف', style=style_a2a2a2)
    sheet.col(3).width = 6000
    sheet.write_merge(20, 21, 3, 3, 'اسم الممول', style=style_a2a2a2)
    sheet.col(4).width = 6000
    sheet.write_merge(20, 21, 4, 4, 'العنوان', style=style_a2a2a2)
    sheet.write_merge(20, 20, 5, 6, 'المأمورية المختصة', style=style_a2a2a2)

    sheet.col(5).width = 3500
    sheet.write(21, 5, 'مأمورية', style=style_a2a2a2)
    sheet.col(6).width = 1100
    sheet.write(21, 6, 'كود', style=style_a2a2a2)
    sheet.write_merge(20, 21, 7, 7, 'تاريخ التعامل', style=style_a2a2a2)
    sheet.write_merge(20, 20, 8, 9, 'المأمورية المختصة', style=style_a2a2a2)
    sheet.col(8).width = 5000
    sheet.write(21, 8, 'ط . التعامل', style=style_a2a2a2)
    sheet.col(9).width = 1000
    sheet.write(21, 9, 'كود', style=style_a2a2a2)
    sheet.write_merge(20, 21, 10, 10, 'القيمة الاجمالية للتعامل', style=style_a2a2a2)
    sheet.write_merge(20, 20, 11, 12, 'الخصومات', style=style_a2a2a2)
    sheet.col(11).width = 2000
    sheet.write(21, 11, 'نوع الخصم', style=style_a2a2a2)
    sheet.col(12).width = 1000
    sheet.write(21, 12, 'كود', style=style_a2a2a2)
    sheet.write_merge(20, 21, 13, 13, 'القيمة الصافية للتعامل', style=style_a2a2a2)
    sheet.col(14).width = 1500
    sheet.write_merge(20, 21, 14, 14, 'نسبة الخصم', style=style_a2a2a2)
    sheet.write_merge(20, 21, 15, 15, 'المحصل لحساب الضريبة', style=style_a2a2a2)
    return sheet


def get_interval_date(_date):
    return '30-' + str(_date.month) + '-' + str(_date.year)


def write_dictionary_in_sheet(margin, sheet, dict_data):
    total = 0
    count = 0
    for value in dict_data.values():
        sheet.write(margin + count + 1, 0, count + 1)
        sheet.write(margin + count + 1, 1, value['partner_vat'] if value['partner_vat'] else '')
        sheet.write(margin + count + 1, 2, value['partner_tax_file'] if value['partner_tax_file'] else '')
        sheet.write(margin + count + 1, 3, value['partner_name'] if value['partner_name'] else '')
        sheet.write(margin + count + 1, 4, value['partner_address'] if value['partner_address'] else '')
        sheet.write(margin + count + 1, 5,
                    value['partner_tax_department'] if value['partner_tax_department'] else '')
        sheet.write(margin + count + 1, 7, str(value['date_invoice']) if value['date_invoice'] else '')
        sheet.write(margin + count + 1, 8, value['tax_name'] if value['tax_name'] else '')
        sheet.write(margin + count + 1, 13, value['amount'] if value['amount'] else '')
        sheet.write(margin + count + 1, 14, value['tax_ratio'] if value['tax_ratio'] else '')
        total += value['tax_value']
        sheet.write(margin + count + 1, 15, value['tax_value'] if value['tax_value'] else '')
        # sheet.write(margin + count + 1, 17, str(progress_invoice.id))
        count += 1
    sheet.write_merge(6, 6, 11, 14, round(total, 2))
    return sheet


class SaleOrderReport(models.TransientModel):
    _name = "form41.summery.report"

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
    data = fields.Char('Name', size=256)
    file_name = fields.Binary('Report File', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    _sql_constraints = [
        ('check', 'CHECK((start_date <= end_date))', "End date must be greater then start date")
    ]

    def _read_data(self):
        progress_invoice_journal = self.env['account.journal'].search([('name', 'ilike', 'Progress Invoice')])
        vendor_bills_journal = self.env['account.journal'].search([('name', 'ilike', 'Vendor Bills')])
        almoshtryat_journal = self.env['account.journal'].search([('name', '=', 'المشتريات')])
        moshtryat_journal = self.env['account.journal'].search([('name', '=', 'مشتريات')])
        journals = []
        all_journals = progress_invoice_journal + vendor_bills_journal + almoshtryat_journal + moshtryat_journal
        for item in all_journals:
            journals.append(item.id)
        domain = [('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                  ('journal_id.id', 'in', journals),
                  ('state', 'in', ['open', 'paid', 'in_payment']), ]
        return self.env['account.invoice'].search(domain)

    def _read_journal_items(self):
        cash_journal = self.env['account.journal'].search([('type', '=', 'cash')])
        cash_journal_ids = []
        for item in cash_journal:
            cash_journal_ids.append(item.id)
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date),
                  ('journal_id.id', 'in', cash_journal_ids)]
        return self.env['account.move'].search(domain)

    def _read_mortad_journal_items(self):
        mortad_moshtryat_journal = self.env['account.journal'].search([('name', '=', 'مرتد المشتريات')])
        mortad_journal_ids = []
        for item in mortad_moshtryat_journal:
            mortad_journal_ids.append(item.id)
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date),
                  ('journal_id.id', 'in', mortad_journal_ids)]
        return self.env['account.move'].search(domain)

    @api.multi
    def action_report(self):

        workbook = xlwt.Workbook(encoding="UTF-8")

        sheet = workbook.add_sheet("Form 41 by Summery Report")
        sheet.cols_right_to_left = True
        sheet = report_header(workbook, sheet)
        progress_invoices = self._read_data()

        margin = 21

        report_dict = {}
        for progress_invoice in progress_invoices:
            for invoice_line in progress_invoice.invoice_line_ids:
                for tax_line in invoice_line.invoice_line_tax_ids:
                    tax_type = tax_line.tax_type

                    if tax_type == 'أ.ت.ص' and invoice_line.price_subtotal != 0:
                        tax_value = abs(round(0.01 * tax_line.amount * invoice_line.price_subtotal, 2))
                        interval_date = get_interval_date(progress_invoice.date_invoice)
                        partner_tax_type_key = tax_line.name + '-' + str(progress_invoice.partner_id.id) + '-' + interval_date
                        if invoice_line.price_subtotal < 0:
                            tax_value = - tax_value
                        if partner_tax_type_key in report_dict.keys():
                            report_dict[partner_tax_type_key]['tax_value'] += tax_value
                            report_dict[partner_tax_type_key]['amount'] += invoice_line.price_subtotal
                        else:
                            tmp_values = {}
                            tmp_values['partner_vat'] = progress_invoice.partner_id.vat
                            tmp_values['partner_tax_file'] = progress_invoice.partner_id.tax_file
                            tmp_values['partner_name'] = progress_invoice.partner_id.name
                            tmp_values['partner_address'] = progress_invoice.partner_id.street
                            tmp_values['partner_tax_department'] = progress_invoice.partner_id.tax_department
                            tmp_values['date_invoice'] = interval_date
                            tmp_values['tax_name'] = tax_line.name
                            tmp_values['amount'] = invoice_line.price_subtotal
                            tmp_values['tax_ratio'] = abs(tax_line.amount)
                            tmp_values['tax_value'] = tax_value
                            report_dict[partner_tax_type_key] = tmp_values

        account_moves = self._read_journal_items()

        for account_move in account_moves:
            journal_items = account_move.line_ids
            account_12014_flag = False
            account_21011002_flag = False
            for item in journal_items:
                if item.debit != 0:
                    amount = round(item.debit, 2)
                if item.account_id.code == '12014':
                    account_12014_flag = True
                if item.account_id.code == '21011002':
                    account_21011002_flag = True
                    partner = item.partner_id
                    tax_value = round(item.credit, 2)
                    tax_name = item.name
                    tax_amount = item.tax_line_id.amount

            if account_12014_flag and account_21011002_flag:

                interval_date = get_interval_date(account_move.date)
                partner_tax_type_key = tax_name + '-' + str(partner.id) + '-' + interval_date

                if partner_tax_type_key in report_dict.keys():
                    report_dict[partner_tax_type_key]['tax_value'] += tax_value
                    report_dict[partner_tax_type_key]['amount'] += amount
                else:
                    tmp_values = {}
                    tmp_values['partner_vat'] = partner.vat
                    tmp_values['partner_tax_file'] = partner.tax_file
                    tmp_values['partner_name'] = partner.name
                    tmp_values['partner_address'] = partner.street
                    tmp_values['partner_tax_department'] = partner.tax_department
                    tmp_values['date_invoice'] = interval_date
                    tmp_values['tax_name'] = tax_name
                    tmp_values['amount'] = amount
                    tmp_values['tax_ratio'] = abs(tax_amount)
                    tmp_values['tax_value'] = tax_value
                    report_dict[partner_tax_type_key] = tmp_values

        mortads = self._read_mortad_journal_items()
        for mortad in mortads:
            journal_items = mortad.line_ids
            tax_flag = False
            for item in journal_items:
                for tax in item.tax_ids:
                    if tax.tax_type == 'أ.ت.ص':
                        tax_flag = True
                        tax_name = tax.name
                        tax_amount = -tax.amount / 100
            if tax_flag:
                partner = item.partner_id
                if item.debit != 0:
                    amount = round(item.debit, 2)
                if item.credit != 0:
                    amount = - round(item.credit, 2)

                tax_value = tax_amount * amount
                interval_date = get_interval_date(mortad.date)
                partner_tax_type_key = tax_name + '-' + str(partner.id) + '-' + interval_date

                if partner_tax_type_key in report_dict.keys():
                    report_dict[partner_tax_type_key]['tax_value'] += tax_value
                    report_dict[partner_tax_type_key]['amount'] += amount
                else:
                    tmp_values = {}
                    tmp_values['partner_vat'] = partner.vat
                    tmp_values['partner_tax_file'] = partner.tax_file
                    tmp_values['partner_name'] = partner.name
                    tmp_values['partner_address'] = partner.street
                    tmp_values['partner_tax_department'] = partner.tax_department
                    tmp_values['date_invoice'] = interval_date
                    tmp_values['tax_name'] = tax_name
                    tmp_values['amount'] = amount
                    tmp_values['tax_ratio'] = abs(tax_amount)
                    tmp_values['tax_value'] = tax_value
                    report_dict[partner_tax_type_key] = tmp_values

        write_dictionary_in_sheet(margin, sheet, report_dict)

        fp = StringIO()
        file_name = '/tmp/Form 41 by Summery Report.xls'
        workbook.save(file_name)
        file = open(file_name, "rb")
        file_data = file.read()
        out = base64.encodebytes(file_data)
        self.write({'state': 'get', 'file_name': out, 'data': 'Form 41 by Summery Report.xls'})
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'form41.summery.report',
            'name': 'Form 41 by Summery Report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

