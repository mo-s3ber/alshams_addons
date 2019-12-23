# -*- coding: utf-8 -*-

import xlwt
import base64
import calendar
from io import StringIO
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import date
import datetime


class SaleOrderReport(models.TransientModel):
    _name = "sale.order.report"

    location_id = fields.Many2one('stock.location', 'From')
    product_id = fields.Many2one('product.product')
    stock_location_id = fields.Many2one('stock.location', 'Stock Location')
    loca_dest_id = fields.Many2one('stock.location', 'To')
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
    sale_order_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Product Move Excel Report', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    _sql_constraints = [
        ('check', 'CHECK((start_date <= end_date))', "End date must be greater then start date")
    ]

    @api.multi
    def chk_field(self):
        if len(self._context.get('active_ids', [])) > 0:
            self.chk_activ_ids = True
        else:
            self.chk_activ_ids = False

    chk_activ_ids = fields.Boolean(compute='chk_field')

    @api.multi
    def action_sale_report(self):
        context = self.env.context
        # if context.get('location'):
        #     print(context.get('location'))
        # else:
        #     print('NNNNo')
        file = StringIO()
        if len(self._context.get('active_ids', [])) > 0:
            product_move = self.env['stock.move.line'].browse(self._context['active_ids'])
        else:
            wizard = self.env['sale.order.report'].browse(self.id)

            stock_moves = self.env['stock.move'].search([('company_id', '=', self.env.user.company_id.id)])
            domain = [('move_id', 'in', stock_moves.ids), ('product_id', '=', self.product_id.id),
                      ('state', '=', 'done'), '|', ('location_id', '=', wizard.stock_location_id.id),
                      ('location_dest_id', '=', wizard.stock_location_id.id)]

            product_move = self.env['stock.move.line'].search(domain)

        workbook = xlwt.Workbook()
        sheets = workbook.add_sheet(str("Product Moves"))
        if product_move:
            row = 0
            format2 = xlwt.easyxf('font:bold True;align: horiz left')
            sheets.write(row, 0, 'Date', format2)
            sheets.write(row, 1, 'Reference', format2)
            sheets.write(row, 2, 'Product', format2)
            sheets.write(row, 3, 'From', format2)
            sheets.write(row, 4, 'To', format2)
            sheets.write(row, 5, 'Done Qty2', format2)
            sheets.write(row, 6, 'Out', format2)
            sheets.write(row, 7, 'In', format2)
            sheets.write(row, 8, 'Balance', format2)
            sheets.write(row, 9, 'Partner', format2)
            # sheets.write(row, 8, 'Quantity Done', format2)
            # sheets.write(row, 9, 'Status', format2)
            sheets.write(row, 10, 'Cost', format2)

            sheets.write(row, 11, 'Source Document', format2)

            for counter, rec in enumerate(product_move):
                if rec.move_id.is_force_cost:
                    cost = rec.move_id.price_unit
                else:
                    cost = rec.move_id.unit_inventory_cost
                count = 0
                try:
                    sheets.write(row + 1, count,
                                datetime.datetime.strptime(str(rec.picking_id.date_done), '%Y-%m-%d %H:%M:%S').strftime(
                                     '%Y-%m-%d %H:%M:%S'), format2)
                except Exception as e:
                    sheets.write(row + 1, count,datetime.datetime.strptime(str(rec.date), '%Y-%m-%d %H:%M:%S').strftime(
                                     '%Y-%m-%d %H:%M:%S')
                                 ,format2)

                sheets.write(row + 1, count + 1, rec.reference, format2)
                sheets.write(row + 1, count + 2, rec.product_id.name, format2)
                sheets.write(row + 1, count + 3, rec.location_id.complete_name, format2)
                sheets.write(row + 1, count + 4, rec.location_dest_id.complete_name, format2)
                # rec.calculate_qty(self.stock_location_id)

                # product_move[counter - 1].done_qty_2 = 0 done_quan = 0 if "INV" in rec.reference else print('No')
                done_quan = 0 if counter == 0 else product_move[counter - 1].done_qty_2 + done_quan
                # print('1',rec.done_qty_2)
                # print('2',done_quan)
                # print('2',rec.done_qty_2)
                # if "INV" in rec.reference:
                #     test = rec.product_uom_qty
                # else:
                #     test = rec.done_qty_2 + done_quan

                sheets.write(row + 1, count + 5, rec.done_qty_2, format2)
                if "INV" in rec.reference:
                    sheets.write(row + 1, count + 6, "", format2)
                else:
                    if wizard.stock_location_id.id == rec.location_id.id:
                        sheets.write(row + 1, count + 6, round(rec.done_qty_2, 2), format2)
                    else:
                        sheets.write(row + 1, count + 6, '', format2)
                if "INV" in rec.reference:
                    sheets.write(row + 1, count + 7, "", format2)
                else:
                    if wizard.stock_location_id.id == rec.location_dest_id.id:
                        sheets.write(row + 1, count + 7, round(rec.done_qty_2, 2), format2)
                    else:
                        sheets.write(row + 1, count + 7, '', format2)
                # if "INV" in rec.reference:
                if "INV" in rec.reference:
                    x = self.env['stock.inventory'].search([('write_date','=',rec.write_date)]).id
                    # print(x)
                    # print(rec.write_date)
                    sheets.write(row + 1, count + 8, self.env['stock.inventory.line'].search([('product_id','=',rec.product_id.id),('location_id','=',self.stock_location_id.id),('inventory_id','=',x)]).product_qty, format2)
                else:
                    sheets.write(row + 1, count + 8, rec.done_qty_2 + done_quan, format2)
                # else:
                    # sheets.write(row + 1, count + 8, rec.done_qty_2 + done_quan, format2)

                sheets.write(row + 1, count + 9, rec.my_partner.name, format2)

                # sheets.write(row + 1, count + 8, rec.qty_done, format2)
                #
                # sheets.write(row + 1, count + 9, rec.state, format2)
                sheets.write(row + 1, count + 10, round(cost, 2), format2)

                # sheets.write(row + 1, count + 11, rec.picking_id.origin1.name if rec.picking_id.origin1.name else '',
                #              format2)
                row += 1
        else:
            raise Warning("Currently No Product Move!!")
        filename = ('/tmp/Product Move Report' + '.xls')
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodebytes(file_data)
        self.write({'state': 'get', 'file_name': out, 'sale_order_data': 'Product Move Report.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
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

            done_quan = 0 if counter == 0 else self[counter - 1].done_qty_2 + done_quan
            
            sheets.write(row + 1, count + 5, done_quan, format2)
            sheets.write(row + 1, count + 6, rec.done_qty_2, format2)
            sheets.write(row + 1, count + 7, rec.done_qty_2 + done_quan, format2)

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

