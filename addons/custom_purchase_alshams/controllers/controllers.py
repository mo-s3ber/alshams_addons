# -*- coding: utf-8 -*-
from odoo import http

# class CustomPurchaseAlshams(http.Controller):
#     @http.route('/custom_purchase_alshams/custom_purchase_alshams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_purchase_alshams/custom_purchase_alshams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_purchase_alshams.listing', {
#             'root': '/custom_purchase_alshams/custom_purchase_alshams',
#             'objects': http.request.env['custom_purchase_alshams.custom_purchase_alshams'].search([]),
#         })

#     @http.route('/custom_purchase_alshams/custom_purchase_alshams/objects/<model("custom_purchase_alshams.custom_purchase_alshams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_purchase_alshams.object', {
#             'object': obj
#         })