# -*- coding: utf-8 -*-
from odoo import http

# class TreasuryStatementReport(http.Controller):
#     @http.route('/treasury_statement_report/treasury_statement_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/treasury_statement_report/treasury_statement_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('treasury_statement_report.listing', {
#             'root': '/treasury_statement_report/treasury_statement_report',
#             'objects': http.request.env['treasury_statement_report.treasury_statement_report'].search([]),
#         })

#     @http.route('/treasury_statement_report/treasury_statement_report/objects/<model("treasury_statement_report.treasury_statement_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('treasury_statement_report.object', {
#             'object': obj
#         })