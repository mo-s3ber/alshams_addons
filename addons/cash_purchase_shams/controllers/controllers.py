# -*- coding: utf-8 -*-
from odoo import http

# class CashPurchaseShams(http.Controller):
#     @http.route('/cash_purchase_shams/cash_purchase_shams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cash_purchase_shams/cash_purchase_shams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cash_purchase_shams.listing', {
#             'root': '/cash_purchase_shams/cash_purchase_shams',
#             'objects': http.request.env['cash_purchase_shams.cash_purchase_shams'].search([]),
#         })

#     @http.route('/cash_purchase_shams/cash_purchase_shams/objects/<model("cash_purchase_shams.cash_purchase_shams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cash_purchase_shams.object', {
#             'object': obj
#         })