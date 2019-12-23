# -*- coding: utf-8 -*-
from odoo import http

# class BankAnalyticAccount(http.Controller):
#     @http.route('/bank_analytic_account/bank_analytic_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bank_analytic_account/bank_analytic_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bank_analytic_account.listing', {
#             'root': '/bank_analytic_account/bank_analytic_account',
#             'objects': http.request.env['bank_analytic_account.bank_analytic_account'].search([]),
#         })

#     @http.route('/bank_analytic_account/bank_analytic_account/objects/<model("bank_analytic_account.bank_analytic_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bank_analytic_account.object', {
#             'object': obj
#         })