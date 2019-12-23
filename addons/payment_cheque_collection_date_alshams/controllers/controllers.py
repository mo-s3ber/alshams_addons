# -*- coding: utf-8 -*-
from odoo import http

# class PaymentChequeCollectionDate(http.Controller):
#     @http.route('/payment_cheque_collection_date/payment_cheque_collection_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_cheque_collection_date/payment_cheque_collection_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_cheque_collection_date.listing', {
#             'root': '/payment_cheque_collection_date/payment_cheque_collection_date',
#             'objects': http.request.env['payment_cheque_collection_date.payment_cheque_collection_date'].search([]),
#         })

#     @http.route('/payment_cheque_collection_date/payment_cheque_collection_date/objects/<model("payment_cheque_collection_date.payment_cheque_collection_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_cheque_collection_date.object', {
#             'object': obj
#         })