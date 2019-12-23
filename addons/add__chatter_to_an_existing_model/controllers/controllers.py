# -*- coding: utf-8 -*-
from odoo import http

# class AddChatterToAnExistingModel(http.Controller):
#     @http.route('/add__chatter_to_an_existing_model/add__chatter_to_an_existing_model/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add__chatter_to_an_existing_model/add__chatter_to_an_existing_model/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add__chatter_to_an_existing_model.listing', {
#             'root': '/add__chatter_to_an_existing_model/add__chatter_to_an_existing_model',
#             'objects': http.request.env['add__chatter_to_an_existing_model.add__chatter_to_an_existing_model'].search([]),
#         })

#     @http.route('/add__chatter_to_an_existing_model/add__chatter_to_an_existing_model/objects/<model("add__chatter_to_an_existing_model.add__chatter_to_an_existing_model"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add__chatter_to_an_existing_model.object', {
#             'object': obj
#         })