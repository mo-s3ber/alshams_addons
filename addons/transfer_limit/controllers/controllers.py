# -*- coding: utf-8 -*-
from odoo import http

# class TransferLimit(http.Controller):
#     @http.route('/transfer_limit/transfer_limit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transfer_limit/transfer_limit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transfer_limit.listing', {
#             'root': '/transfer_limit/transfer_limit',
#             'objects': http.request.env['transfer_limit.transfer_limit'].search([]),
#         })

#     @http.route('/transfer_limit/transfer_limit/objects/<model("transfer_limit.transfer_limit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transfer_limit.object', {
#             'object': obj
#         })