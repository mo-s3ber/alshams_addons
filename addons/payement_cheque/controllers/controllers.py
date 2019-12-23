# -*- coding: utf-8 -*-
from odoo import http

# class PayementCheque(http.Controller):
#     @http.route('/payement_cheque/payement_cheque/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payement_cheque/payement_cheque/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payement_cheque.listing', {
#             'root': '/payement_cheque/payement_cheque',
#             'objects': http.request.env['payement_cheque.payement_cheque'].search([]),
#         })

#     @http.route('/payement_cheque/payement_cheque/objects/<model("payement_cheque.payement_cheque"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payement_cheque.object', {
#             'object': obj
#         })