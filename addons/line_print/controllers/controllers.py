# -*- coding: utf-8 -*-
from odoo import http

# class LinePrint(http.Controller):
#     @http.route('/line_print/line_print/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/line_print/line_print/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('line_print.listing', {
#             'root': '/line_print/line_print',
#             'objects': http.request.env['line_print.line_print'].search([]),
#         })

#     @http.route('/line_print/line_print/objects/<model("line_print.line_print"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('line_print.object', {
#             'object': obj
#         })