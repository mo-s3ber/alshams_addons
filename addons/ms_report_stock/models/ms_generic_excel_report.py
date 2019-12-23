from odoo import fields, models, api

class MsGenericExcelReport(models.Model):
    _inherit = 'ms.generic.excel.report'

    @api.multi
    def finalize_query(self, query):
        query = super(MsGenericExcelReport, self).finalize_query(query)
        if self.code == 'report_stock' :
            where = " 1=1 "
            wizard_id = self._context.get('wizard_id', False)
            if wizard_id :
                if wizard_id.report_stock_product_ids :
                    where += " and sq.product_id in %s "%str(tuple(wizard_id.report_stock_product_ids.ids)).replace(',)',')')
                if wizard_id.report_stock_location_ids :
                    where += " and sq.location_id in %s "%str(tuple(wizard_id.report_stock_location_ids.ids)).replace(',)',')')
            query = """
                SELECT
                    pt.name, 
                    sl.complete_name, 
                    sq.quantity 
                FROM 
                    stock_quant sq 
                LEFT JOIN 
                    stock_location sl on sl.id = sq.location_id 
                LEFT JOIN 
                    product_product pp on pp.id = sq.product_id 
                LEFT JOIN
                    product_template pt on pt.id = pp.product_tmpl_id
                WHERE sl.usage = 'internal' and %s
            """%where
        return query

    @api.multi
    def static_header(self):
        header_data = super(MsGenericExcelReport, self).static_header()
        if self.code == 'report_stock' :
            header_data = [
                'Product',
                'Location',
                'Qty',
            ]
        return header_data
