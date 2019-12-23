# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseSubconntractReports(http.Controller):
#     @http.route('/purchase_subconntract_reports/purchase_subconntract_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_subconntract_reports/purchase_subconntract_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_subconntract_reports.listing', {
#             'root': '/purchase_subconntract_reports/purchase_subconntract_reports',
#             'objects': http.request.env['purchase_subconntract_reports.purchase_subconntract_reports'].search([]),
#         })

#     @http.route('/purchase_subconntract_reports/purchase_subconntract_reports/objects/<model("purchase_subconntract_reports.purchase_subconntract_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_subconntract_reports.object', {
#             'object': obj
#         })