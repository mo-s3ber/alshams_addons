# -*- coding: utf-8 -*-
from odoo import http

# class CustomProgressInvoice(http.Controller):
#     @http.route('/custom_progress_invoice/custom_progress_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_progress_invoice/custom_progress_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_progress_invoice.listing', {
#             'root': '/custom_progress_invoice/custom_progress_invoice',
#             'objects': http.request.env['custom_progress_invoice.custom_progress_invoice'].search([]),
#         })

#     @http.route('/custom_progress_invoice/custom_progress_invoice/objects/<model("custom_progress_invoice.custom_progress_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_progress_invoice.object', {
#             'object': obj
#         })