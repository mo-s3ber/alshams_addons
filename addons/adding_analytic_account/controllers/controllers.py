# -*- coding: utf-8 -*-
from odoo import http

# class AddingAnalyticAccount(http.Controller):
#     @http.route('/adding_analytic_account/adding_analytic_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/adding_analytic_account/adding_analytic_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('adding_analytic_account.listing', {
#             'root': '/adding_analytic_account/adding_analytic_account',
#             'objects': http.request.env['adding_analytic_account.adding_analytic_account'].search([]),
#         })

#     @http.route('/adding_analytic_account/adding_analytic_account/objects/<model("adding_analytic_account.adding_analytic_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('adding_analytic_account.object', {
#             'object': obj
#         })