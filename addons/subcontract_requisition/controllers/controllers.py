# -*- coding: utf-8 -*-
from odoo import http

# class SubcontractRequisition(http.Controller):
#     @http.route('/subcontract_requisition/subcontract_requisition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/subcontract_requisition/subcontract_requisition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('subcontract_requisition.listing', {
#             'root': '/subcontract_requisition/subcontract_requisition',
#             'objects': http.request.env['subcontract_requisition.subcontract_requisition'].search([]),
#         })

#     @http.route('/subcontract_requisition/subcontract_requisition/objects/<model("subcontract_requisition.subcontract_requisition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('subcontract_requisition.object', {
#             'object': obj
#         })