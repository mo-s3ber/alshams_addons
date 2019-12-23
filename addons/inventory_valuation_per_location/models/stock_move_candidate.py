# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class StockMoveCandidate(models.Model):

    _name = 'stock.move.candidate'

    move_id = fields.Many2one('stock.move', 'Move')
    candidate_move_id = fields.Many2one('stock.move', 'Move')
    price_unit = fields.Float('Price Unit')
    quantity = fields.Float('Quantity')
    value = fields.Float('Value')