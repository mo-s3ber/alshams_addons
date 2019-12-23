# -*- coding: utf-8 -*-
from odoo import http

# class Payment-report(http.Controller):
#     @http.route('/payment-report/payment-report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment-report/payment-report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment-report.listing', {
#             'root': '/payment-report/payment-report',
#             'objects': http.request.env['payment-report.payment-report'].search([]),
#         })

#     @http.route('/payment-report/payment-report/objects/<model("payment-report.payment-report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment-report.object', {
#             'object': obj
#         })