# -*- coding: utf-8 -*-
from odoo import http

# class ProductDoneQtyStock(http.Controller):
#     @http.route('/product_done_qty_stock/product_done_qty_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_done_qty_stock/product_done_qty_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_done_qty_stock.listing', {
#             'root': '/product_done_qty_stock/product_done_qty_stock',
#             'objects': http.request.env['product_done_qty_stock.product_done_qty_stock'].search([]),
#         })

#     @http.route('/product_done_qty_stock/product_done_qty_stock/objects/<model("product_done_qty_stock.product_done_qty_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_done_qty_stock.object', {
#             'object': obj
#         })