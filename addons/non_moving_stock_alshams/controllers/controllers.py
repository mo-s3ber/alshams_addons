# -*- coding: utf-8 -*-
from odoo import http

# class NonMovingStockAlshams(http.Controller):
#     @http.route('/non_moving_stock_alshams/non_moving_stock_alshams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/non_moving_stock_alshams/non_moving_stock_alshams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('non_moving_stock_alshams.listing', {
#             'root': '/non_moving_stock_alshams/non_moving_stock_alshams',
#             'objects': http.request.env['non_moving_stock_alshams.non_moving_stock_alshams'].search([]),
#         })

#     @http.route('/non_moving_stock_alshams/non_moving_stock_alshams/objects/<model("non_moving_stock_alshams.non_moving_stock_alshams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('non_moving_stock_alshams.object', {
#             'object': obj
#         })