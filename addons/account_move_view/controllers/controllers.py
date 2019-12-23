# -*- coding: utf-8 -*-
from odoo import http

# class AccountMoveView(http.Controller):
#     @http.route('/account_move_view/account_move_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_move_view/account_move_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_move_view.listing', {
#             'root': '/account_move_view/account_move_view',
#             'objects': http.request.env['account_move_view.account_move_view'].search([]),
#         })

#     @http.route('/account_move_view/account_move_view/objects/<model("account_move_view.account_move_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_move_view.object', {
#             'object': obj
#         })