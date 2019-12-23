# -*- coding: utf-8 -*-
from odoo import http

# class SplitJournalEntry(http.Controller):
#     @http.route('/split_journal_entry/split_journal_entry/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/split_journal_entry/split_journal_entry/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('split_journal_entry.listing', {
#             'root': '/split_journal_entry/split_journal_entry',
#             'objects': http.request.env['split_journal_entry.split_journal_entry'].search([]),
#         })

#     @http.route('/split_journal_entry/split_journal_entry/objects/<model("split_journal_entry.split_journal_entry"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('split_journal_entry.object', {
#             'object': obj
#         })