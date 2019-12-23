# -*- coding: utf-8 -*-
from odoo import http

# class PoAccTax(http.Controller):
#     @http.route('/po_acc_tax/po_acc_tax/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/po_acc_tax/po_acc_tax/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('po_acc_tax.listing', {
#             'root': '/po_acc_tax/po_acc_tax',
#             'objects': http.request.env['po_acc_tax.po_acc_tax'].search([]),
#         })

#     @http.route('/po_acc_tax/po_acc_tax/objects/<model("po_acc_tax.po_acc_tax"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('po_acc_tax.object', {
#             'object': obj
#         })