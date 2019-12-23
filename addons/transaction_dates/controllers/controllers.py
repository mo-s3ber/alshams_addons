# -*- coding: utf-8 -*-
from odoo import http

# class TransactionDates(http.Controller):
#     @http.route('/transaction_dates/transaction_dates/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transaction_dates/transaction_dates/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transaction_dates.listing', {
#             'root': '/transaction_dates/transaction_dates',
#             'objects': http.request.env['transaction_dates.transaction_dates'].search([]),
#         })

#     @http.route('/transaction_dates/transaction_dates/objects/<model("transaction_dates.transaction_dates"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transaction_dates.object', {
#             'object': obj
#         })