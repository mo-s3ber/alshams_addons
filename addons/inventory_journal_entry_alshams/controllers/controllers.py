# -*- coding: utf-8 -*-
from odoo import http

# class InventoryJournalEntryAlshams(http.Controller):
#     @http.route('/inventory_journal_entry_alshams/inventory_journal_entry_alshams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_journal_entry_alshams/inventory_journal_entry_alshams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_journal_entry_alshams.listing', {
#             'root': '/inventory_journal_entry_alshams/inventory_journal_entry_alshams',
#             'objects': http.request.env['inventory_journal_entry_alshams.inventory_journal_entry_alshams'].search([]),
#         })

#     @http.route('/inventory_journal_entry_alshams/inventory_journal_entry_alshams/objects/<model("inventory_journal_entry_alshams.inventory_journal_entry_alshams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_journal_entry_alshams.object', {
#             'object': obj
#         })