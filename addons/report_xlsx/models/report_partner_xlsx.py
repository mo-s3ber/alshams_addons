

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.report_xlsx.order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        # expenses = (
        #     ['Rent', 1000],
        #     ['Gas', 100],
        #     ['Food', 300],
        #     ['Gym', 50],
        # )

        row = 0
        col = 0

        # sale_obj = self.env['sale.order'].search([('id', '=', self.env.context['active_id'])])
        # raise Warning(sale_obj)
        # print(sale_obj)

        # sale_obj = self.env['sale.order'].search([('id', '=', self._context.get('active_id'))])


        # sale_obb = self.env['sale.order'].browse(self._context.get('active_id')).ids


        # sale_obj = self.env['sale.order'].search([])
        #
        # print(sale_obj)

        # print('MMMMMMMMMMMMMMMMMMMM',sale_obj)

        for obj in partners:
            sheet = workbook.add_worksheet('Report')
            bold = workbook.add_format({'bold': True})
            # for item, cost in (expenses):
            #     sheet.write(row, col, item)
            #     sheet.write(row, col + 1, cost)
            # row += 1
            # sheet.write(row, col,'name')

            # print (obj.id, 'DDDDDDDDDDDDDDDDDDDDDDDD')
            # print (obj.order_line.name, 'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

            sheet.write(row, col, obj.name, bold)
            sheet.write(row + 2, col, 'Customer', bold)
            sheet.write(row+2, col + 2, obj.partner_id.name, bold)


            # sheet.write(row + 1, col + 8, 'Confirmation Date', bold)
            # sheet.write(row + 1, col + 10, obj.confirmation_date, bold)

            sheet.write(row + 2, col + 8, 'Expiration Date', bold)
            sheet.write(row + 2, col + 10, obj.validity_date, bold)



            sheet.write(row + 5, col + 8, 'Payment Terms', bold)
            sheet.write(row + 5, col + 10, obj.payment_term_id.name, bold)


            # sheet.write(row + 8, col + 2, obj.amount_untaxed, bold)
            # sheet.write(row + 8, col + 3, obj.amount_tax, bold)
            # sheet.write(row + 8, col + 4, obj.amount_total, bold)
            # sheet.write(row + 4, col + 1, obj.user_id.name, bold)
            # sheet.write(row + 5, col + 1, obj.team_id.name, bold)
            # sheet.write(row + 6, col + 1, obj.fiscal_position_id.name, bold)
            # sheet.write(row + 7, col + 1, obj.invoice_status, bold)
            # sheet.write(row + 8, col + 1, obj.origin, bold)
            # sheet.write(row + 9, col + 1, obj.client_order_ref, bold)

            sheet.write(row + 7, col , 'Order Lines', bold)
            sheet.write(row + 10, col , 'Product', bold)
            sheet.write(row + 10, col + 4, 'Description', bold)
            sheet.write(row + 10, col + 8, 'Ordered QTY', bold)
            sheet.write(row + 10, col + 10, 'Unit Price', bold)
            sheet.write(row + 10, col + 12, 'Taxes', bold)
            sheet.write(row + 10, col + 14, 'Subtotal', bold)



            for i in obj.order_line:


                sheet.write(row + 12, col , i.product_id.name, bold)
                sheet.write(row + 12, col+4, i.name, bold)
                sheet.write(row + 12, col + 8, i.product_uom_qty, bold)
                sheet.write(row + 12, col + 10, i.price_unit, bold)
                sheet.write(row + 12, col + 12, i.tax_id.name, bold)
                sheet.write(row + 12, col + 14, i.price_subtotal, bold)
                row+=1
                # col+=1

            # sheet.write(row + 7, col + 1, 'Product', bold)
            # sheet.write(row + 12, col + 1, obj.order_line.product_uom_qty, bold)
            # sheet.write(row + 13, col + 1, obj.order_line.price_unit, bold)
            # sheet.write(row + 14, col + 1, obj.order_line.price_subtotal, bold)

            sheet.write(row+21, col+12, 'Untaxed Amount', bold)
            sheet.write(row+22, col+12, 'Taxes', bold)
            sheet.write(row+24, col+12, 'Total', bold)
            sheet.write(row+21, col+14, obj.amount_untaxed, bold)
            sheet.write(row+22, col+14, obj.amount_tax, bold)
            sheet.write(row+24, col+14, obj.amount_total, bold)



            sheet.write(row + 22, col, 'Sales Infromation', bold)
            sheet.write(row + 24, col, 'Sales person')
            sheet.write(row + 25, col, 'Sales Channels')
            sheet.write(row + 26, col, 'Computer Reference')

            sheet.write(row + 24, col + 2, obj.user_id.name)
            sheet.write(row + 25, col + 2, obj.team_id.name)
            sheet.write(row + 26, col + 2, obj.client_order_ref)



            sheet.write(row + 22, col+5, 'Invoicing', bold)
            sheet.write(row + 24, col + 5, 'Date order')
            sheet.write(row + 25, col + 5, 'Fiscal Position')
            sheet.write(row + 24, col + 6, obj.date_order)
            sheet.write(row + 25, col + 6, obj.fiscal_position_id.name)


            # sheet.write(row + 27, col + 1, obj.invoice_status)

            # sheet.write(row + 27, 'Reporting',bold)
            sheet.write(row + 31, col , 'source Document')
            sheet.write(row + 31, col + 2, obj.origin)







        # for s in sale_obj:
        #     sheet.write(row, col, s)


            # sheet.write(0, 0, expenses, bold)
            # sheet.write(0,0,"abdo",bold)
            # sheet.write(0, 0, 'AAAAAAA','BBBBBBBBBBB', bold)
