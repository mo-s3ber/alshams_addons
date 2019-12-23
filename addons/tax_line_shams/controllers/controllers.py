# -*- coding: utf-8 -*-
from odoo import http

# class TaxLineShams(http.Controller):
#     @http.route('/tax_line_shams/tax_line_shams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tax_line_shams/tax_line_shams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tax_line_shams.listing', {
#             'root': '/tax_line_shams/tax_line_shams',
#             'objects': http.request.env['tax_line_shams.tax_line_shams'].search([]),
#         })

#     @http.route('/tax_line_shams/tax_line_shams/objects/<model("tax_line_shams.tax_line_shams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tax_line_shams.object', {
#             'object': obj
#         })