# -*- coding: utf-8 -*-
from odoo import http

# class Digizilla(http.Controller):
#     @http.route('/digizilla/digizilla/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/digizilla/digizilla/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('digizilla.listing', {
#             'root': '/digizilla/digizilla',
#             'objects': http.request.env['digizilla.digizilla'].search([]),
#         })

#     @http.route('/digizilla/digizilla/objects/<model("digizilla.digizilla"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('digizilla.object', {
#             'object': obj
#         })