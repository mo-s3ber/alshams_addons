# -*- coding: utf-8 -*-
from odoo import http

# class ProgressInvoice(http.Controller):
#     @http.route('/progress_invoice/progress_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/progress_invoice/progress_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('progress_invoice.listing', {
#             'root': '/progress_invoice/progress_invoice',
#             'objects': http.request.env['progress_invoice.progress_invoice'].search([]),
#         })

#     @http.route('/progress_invoice/progress_invoice/objects/<model("progress_invoice.progress_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('progress_invoice.object', {
#             'object': obj
#         })