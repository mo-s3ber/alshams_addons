# -*- coding: utf-8 -*-
from odoo import http

# class PrintButton(http.Controller):
#     @http.route('/print_button/print_button/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/print_button/print_button/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('print_button.listing', {
#             'root': '/print_button/print_button',
#             'objects': http.request.env['print_button.print_button'].search([]),
#         })

#     @http.route('/print_button/print_button/objects/<model("print_button.print_button"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('print_button.object', {
#             'object': obj
#         })