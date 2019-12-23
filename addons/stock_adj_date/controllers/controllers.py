# -*- coding: utf-8 -*-
from odoo import http

# class StockAdjDate(http.Controller):
#     @http.route('/stock_adj_date/stock_adj_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_adj_date/stock_adj_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_adj_date.listing', {
#             'root': '/stock_adj_date/stock_adj_date',
#             'objects': http.request.env['stock_adj_date.stock_adj_date'].search([]),
#         })

#     @http.route('/stock_adj_date/stock_adj_date/objects/<model("stock_adj_date.stock_adj_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_adj_date.object', {
#             'object': obj
#         })