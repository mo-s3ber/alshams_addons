# -*- coding: utf-8 -*-
from odoo import http

# class ForceCostAdjView(http.Controller):
#     @http.route('/force_cost_adj_view/force_cost_adj_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/force_cost_adj_view/force_cost_adj_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('force_cost_adj_view.listing', {
#             'root': '/force_cost_adj_view/force_cost_adj_view',
#             'objects': http.request.env['force_cost_adj_view.force_cost_adj_view'].search([]),
#         })

#     @http.route('/force_cost_adj_view/force_cost_adj_view/objects/<model("force_cost_adj_view.force_cost_adj_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('force_cost_adj_view.object', {
#             'object': obj
#         })