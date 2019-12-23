from odoo import fields, models, api

class MsGenericExcelReportWizard(models.TransientModel):
    _inherit = 'ms.generic.excel.report.wizard'
    
    report_stock_location_ids = fields.Many2many('stock.location', string='Location', domain=[('usage','=','internal')])
    report_stock_product_ids = fields.Many2many('product.product', string='Product')
    