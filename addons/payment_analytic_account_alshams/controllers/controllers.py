# -*- coding: utf-8 -*-
from odoo import http

# class PaymentAnalyticAccountAlshams(http.Controller):
#     @http.route('/payment_analytic_account_alshams/payment_analytic_account_alshams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_analytic_account_alshams/payment_analytic_account_alshams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_analytic_account_alshams.listing', {
#             'root': '/payment_analytic_account_alshams/payment_analytic_account_alshams',
#             'objects': http.request.env['payment_analytic_account_alshams.payment_analytic_account_alshams'].search([]),
#         })

#     @http.route('/payment_analytic_account_alshams/payment_analytic_account_alshams/objects/<model("payment_analytic_account_alshams.payment_analytic_account_alshams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_analytic_account_alshams.object', {
#             'object': obj
#         })