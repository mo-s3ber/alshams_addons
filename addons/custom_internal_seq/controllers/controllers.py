# -*- coding: utf-8 -*-
from odoo import http

# class CustomInternalSeq(http.Controller):
#     @http.route('/custom_internal_seq/custom_internal_seq/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_internal_seq/custom_internal_seq/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_internal_seq.listing', {
#             'root': '/custom_internal_seq/custom_internal_seq',
#             'objects': http.request.env['custom_internal_seq.custom_internal_seq'].search([]),
#         })

#     @http.route('/custom_internal_seq/custom_internal_seq/objects/<model("custom_internal_seq.custom_internal_seq"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_internal_seq.object', {
#             'object': obj
#         })