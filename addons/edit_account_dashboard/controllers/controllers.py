# -*- coding: utf-8 -*-
from odoo import http

# class EditAccountDashboard(http.Controller):
#     @http.route('/edit_account_dashboard/edit_account_dashboard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edit_account_dashboard/edit_account_dashboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('edit_account_dashboard.listing', {
#             'root': '/edit_account_dashboard/edit_account_dashboard',
#             'objects': http.request.env['edit_account_dashboard.edit_account_dashboard'].search([]),
#         })

#     @http.route('/edit_account_dashboard/edit_account_dashboard/objects/<model("edit_account_dashboard.edit_account_dashboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edit_account_dashboard.object', {
#             'object': obj
#         })