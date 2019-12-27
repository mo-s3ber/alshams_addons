# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import ValidationError
import base64
import xlsxwriter
import io
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY
from functools import partial
from itertools import chain
from pytz import timezone, utc
from datetime import datetime


def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n


def is_float(n):
    try:
        float_n = float(n)
    except ValueError:
        return False
    else:
        return True

class ProductMoveReport(models.TransientModel):
    _name = "sale.order.report"

    product_id = fields.Many2one('product.product')
    stock_location_id = fields.Many2one('stock.location', 'Stock Location')
    excel_sheet = fields.Binary('Download Report')



    def generate_data(self):
        if self.product_id:
            stock_moves = self.env['stock.move'].search([('company_id', '=', self.env.user.company_id.id)])
            domain = [('move_id', 'in', stock_moves.ids), ('product_id', '=', self.product_id.id),
                      ('state', '=', 'done'), '|', ('location_id', '=', self.stock_location_id.id),
                      ('location_dest_id', '=', self.stock_location_id.id)]
            lines = self.env['stock.move.line'].search(domain)
        return lines

    @api.multi
    def generate_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        custom_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': 8,
            'fg_color': 'white',
        })

        table_header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'center',
            'text_wrap': True,
            'font_size': 10,
            'valign': 'vcenter',
            'fg_color': '#d8d6d6'
        })

        worksheet = workbook.add_worksheet('Moves')
        worksheet.set_paper(9)
        worksheet.set_portrait()
        row = 0
        worksheet.write(row, 0, 'Date', table_header_format)
        worksheet.write(row, 1, 'Reference', table_header_format)
        worksheet.write(row, 2, 'Product', table_header_format)
        worksheet.write(row, 3, 'From', table_header_format)
        worksheet.write(row, 4, 'To', table_header_format)
        worksheet.write(row, 5, 'QTY Done', table_header_format)
        worksheet.write(row, 6, 'Out', table_header_format)
        worksheet.write(row, 7, 'In', table_header_format)
        worksheet.write(row, 8, 'Balance', table_header_format)
        worksheet.write(row, 9, 'Partner', table_header_format)
        worksheet.write(row, 10, 'Cost', table_header_format)
        worksheet.write(row, 11, 'Source Document', table_header_format)

        row +=1
        col = 0
        balance= 0
        if self.generate_data():
            for line in self.generate_data():
                date = str(line.picking_id.date_done)
                worksheet.write(row, col,date , custom_format)
                worksheet.write(row, col+1, str(line.reference), custom_format)
                worksheet.write(row, col+2, str(line.product_id.name), custom_format)
                worksheet.write(row , col+3, line.location_id.complete_name, custom_format)
                worksheet.write(row , col+4, line.location_dest_id.complete_name, custom_format)
                worksheet.write(row, col + 5, line.qty_done, custom_format)
                if self.stock_location_id.id == line.location_id.id:
                    worksheet.write(row, col + 6, line.qty_done, custom_format)
                    balance -= line.qty_done
                else:
                    worksheet.write(row, col + 6, "", custom_format)
                if self.stock_location_id.id == line.location_dest_id.id:
                    worksheet.write(row, col +7, line.qty_done, custom_format)
                    balance += line.qty_done
                else:
                    worksheet.write(row, col + 6, "", custom_format)
                worksheet.write(row, col + 8, balance, custom_format)
                worksheet.write(row, col + 9, line.picking_id.partner_id.name, custom_format)
                worksheet.write(row, col + 10, line.move_id.price_unit, custom_format)
                worksheet.write(row, col + 11, line.picking_id.origin, custom_format)
                row +=1
        else:
            raise ValidationError("Nothing to Print!")

        workbook.close()
        output.seek(0)
        self.write({'excel_sheet': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'Deviation',
            'url': '/web/content/sale.order.report/%s/excel_sheet/Product_Moves_Report.xlsx?download=true' % (self.id),
            'target': 'self'
        }



class ProductMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def action_sale_reports(self):
        file = StringIO()
        final_value = {}
        workbook = xlwt.Workbook()
        sheets = workbook.add_sheet(str("Product Moves"))
        row = 0
        format2 = xlwt.easyxf('font:bold True;align: horiz left')
        sheets.write(row, 0, 'Date', format2)
        sheets.write(row, 0 + 1, 'Reference', format2)
        sheets.write(row, 0 + 2, 'Product', format2)
        sheets.write(row, 0 + 3, 'From', format2)
        sheets.write(row, 0 + 4, 'To', format2)
        sheets.write(row, 0 + 5, 'Done Qty2 before', format2)
        sheets.write(row, 0 + 6, 'Done Qty2', format2)
        sheets.write(row, 0 + 7, 'Done Qty2 after', format2)
        sheets.write(row, 0 + 8, 'Partner', format2)
        sheets.write(row, 0 + 9, 'Quantity Done', format2)
        sheets.write(row, 0 + 10, 'Status', format2)
        for counter, rec in enumerate(self):
            count = 0
            sheets.write(row + 1, count, datetime.datetime.strptime(str(rec.date), '%Y-%m-%d %H:%M:%S').strftime(
                '%Y-%m-%d %H:%M:%S'), format2)
            sheets.write(row + 1, count + 1, rec.reference, format2)
            sheets.write(row + 1, count + 2, rec.product_id.name, format2)
            sheets.write(row + 1, count + 3, rec.location_id.name, format2)
            sheets.write(row + 1, count + 4, rec.location_dest_id.name, format2)

            done_quan = 0 if counter == 0 else self[counter - 1].done_qty + done_quan
            
            sheets.write(row + 1, count + 5, done_quan, format2)
            sheets.write(row + 1, count + 6, rec.done_qty, format2)
            sheets.write(row + 1, count + 7, rec.done_qty+ done_quan, format2)

            sheets.write(row + 1, count + 8, rec.my_partner.name, format2)

            sheets.write(row + 1, count + 9, rec.qty_done, format2)

            sheets.write(row + 1, count + 10, rec.state, format2)
            row += 2

        filename = ('/tmp/Product Move Report' + '.xls')
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodebytes(file_data)
        wiz = self.env['sale.order.report'].create([])
        wiz.write({'state': 'get', 'file_name': out, 'sale_order_data': 'Product Move Report.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz.id,
            'target': 'new',
        }

