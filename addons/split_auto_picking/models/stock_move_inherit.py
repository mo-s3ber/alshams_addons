from odoo import api, fields, models


class Stock_move(models.Model):
    _inherit = 'stock.move'

    def _search_picking_for_assignation(self):
        self.ensure_one()
        # if not self.env.user.company_id.stop_merge:
        #     return super(Stock_move, self)._search_picking_for_assignation()
        picking = self.env['stock.picking'].search([
            ('group_id', '=', self.group_id.id),
            ('origin', '=', self.origin),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        return picking