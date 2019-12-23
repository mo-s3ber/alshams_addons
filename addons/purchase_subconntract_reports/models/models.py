# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_subconntract_reports(models.Model):
    _inherit = 'purchase.order'

    general_condition = fields.Html(default=" احتساب غرامة تأخير بنسبة 1% من قيمه امر التوريد وبحد اقصي 10 %  في حال وصول البضاعة متأخرة عن موعد التسليم<br> البضاعة الموردة يجب ان تكون مطابقة للمواصفات الفنية للمشروع <br>الأسعار عاليه تشمل النقل الي الموقع <br>الأسعار عاليه ثابتة طوال فتره التوريد<br> برجاء كتابة رقم امر التوريد ف الفاتورة")

    general_conditions = fields.Char(default='''احتساب غرامة تأخير بنسبة 1% من قيمه امر التوريد وبحد افصي 10 % في حال وصول البضاعة متأخرة عن موعد التسليم1)...
        2)البضاعة الموردة يجب ان تكون مطابقة للمواصفات الفنية للمشروع...
        3)الأسعار عالية تشمل النقل الي الموقع...
        4)الأسعار عالية تشمل طوال فتره التوريد...
        5)برجاء كتابة رقم امر التوريد ف الفاتورة...''')

    @api.onchange('order_line')
    @api.multi
    def calc_seq(self):
        # raise Warning('AAAAAAAAAAAAA')
        initial = 1
        for re in self.order_line:
            re.line_sequence = initial
            initial += 1
            # print(re.line_sequence, 'DDDDDDDDDDD')

    @api.multi
    def calc_seqe(self):
        # raise Warning('AAAAAAAAAAAAA')
        purchase_obj = self.env['purchase.order'].search([])

        for p in purchase_obj:
            p.general_condition ='''احتساب غرامة تأخير بنسبة 1% من قيمه امر التوريد وبحد افصي 10 % في حال وصول البضاعة متأخرة عن موعد التسليم
            البضاعة الموردة يجب ان تكون مطابقة للمواصفات الفنية للمشروع
    الأسعار عالية تشمل النقل الي الموقع
    الأسعار عالية تشمل طوال فتره التوريد
    برجاء كتابة رقم امر التوريد ف الفاتورة'''

            p.general_conditions = '''اولا احتساب غرامة تأخير بنسبة 1% من قيمه امر التوريد وبحد افصي 10 % في حال وصول البضاعة متأخرة عن موعد التسليم...
        2)البضاعة الموردة يجب ان تكون مطابقة للمواصفات الفنية للمشروع...
        3)الأسعار عالية تشمل النقل الي الموقع...
        4)الأسعار عالية تشمل طوال فتره التوريد...
        5)برجاء كتابة رقم امر التوريد ف الفاتورة...'''


            initial = 1
            for re in p.order_line:
                re.line_sequence = initial
                initial += 1
                # print(re.line_sequence, 'DDDDDDDDDDD')

        product_move_ids = self.env['stock.move.line'].search([])
        picking_ids = self.env['stock.picking'].search([])
        # for pic in picking_ids:
        #     for pro in product_move_ids:
        #         if pic.origin1 and pro.picking_id.id == pic.id:
        #             pro.source_doc = pro.picking_id.origin1.id


        # pick_ids = self.env['purchase.order'].search([('origin')])




class purchaseOrderLineInheritingg(models.Model):
    _inherit = 'purchase.order.line'
    line_sequence = fields.Integer(string="sequence")



class ResUserSegnature(models.Model):
    _inherit = 'res.users'

    signature_im = fields.Binary(
        "Signature Image", attachment=True,
        help="upload image of your signature")


class PurchasePicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def cla_source(self):

        pick_ids = self.env['purchase.order'].search([])#'name','=',self.origin
        stoc_ids = self.env['stock.picking'].search([])#'name','=',self.origin
        print(pick_ids,'PICKKKKKKKKKKKKKK')
        # print(stoc_ids,'SSSSSSSSSSSS')
        # for pi in pick_ids:
        #     for rec in stoc_ids:
        #         if pi.name == rec.origin:
        #             rec.origin1 = pi.id

    @api.multi
    def move_inventory_cost(self):
        for stock_move in self.move_ids_without_package:
            stock_move.product_id.standard_price = stock_move.unit_inventory_cost


class CustomReport(models.Model):
    _inherit = 'account.move'

    def _custom_report_lines(self):
        taxes = self.env['account.tax'].sudo().search([])
        taxes_names = [tax.name for tax in taxes]
        lines_dict = {}
        for line in self.line_ids:
            tmp_dict = {}
            k = line.name if line.name in taxes_names else str(line.id)
            if k not in lines_dict.keys():
                tmp_dict['name'] = line.name
                tmp_dict['analytic_account_id'] = line.analytic_account_id.name
                tmp_dict['credit'] = round(line.credit, 2)
                tmp_dict['debit'] = round(line.debit, 2)
                tmp_dict['account_id'] = line.account_id.name
                tmp_dict['partner_id'] = line.partner_id.name
                lines_dict[k] = tmp_dict
            else:
                lines_dict[k]['credit'] += round(line.credit, 2)
                lines_dict[k]['debit'] += round(line.debit, 2)

        return lines_dict
