# -*- coding: utf-8 -*-
from odoo import http

# class CheckDeposit(http.Controller):
#     @http.route('/check_deposit/check_deposit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/check_deposit/check_deposit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('check_deposit.listing', {
#             'root': '/check_deposit/check_deposit',
#             'objects': http.request.env['check_deposit.check_deposit'].search([]),
#         })

#     @http.route('/check_deposit/check_deposit/objects/<model("check_deposit.check_deposit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('check_deposit.object', {
#             'object': obj
#         })