# -*- coding: utf-8 -*-
from odoo import http

# class TransferReport(http.Controller):
#     @http.route('/transfer_report/transfer_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transfer_report/transfer_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transfer_report.listing', {
#             'root': '/transfer_report/transfer_report',
#             'objects': http.request.env['transfer_report.transfer_report'].search([]),
#         })

#     @http.route('/transfer_report/transfer_report/objects/<model("transfer_report.transfer_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transfer_report.object', {
#             'object': obj
#         })