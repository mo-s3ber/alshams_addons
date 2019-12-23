# -*- coding: utf-8 -*-
from odoo import http

# class Custom(http.Controller):
#     @http.route('/custom_/custom_/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_/custom_/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_.listing', {
#             'root': '/custom_/custom_',
#             'objects': http.request.env['custom_.custom_'].search([]),
#         })

#     @http.route('/custom_/custom_/objects/<model("custom_.custom_"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_.object', {
#             'object': obj
#         })