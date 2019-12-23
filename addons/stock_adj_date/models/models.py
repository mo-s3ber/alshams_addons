# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InventoryAdjasteDate(models.Model):
    _inherit="stock.inventory"

    date = fields.Datetime(
        'Inventory Date',
        readonly=False, required=True,
        default=fields.Datetime.now,
        help="If the inventory adjustment is not validated, date at which the theoritical quantities have been checked.\n"
             "If the inventory adjustment is validated, date at which the inventory adjustment has been validated.")




    def action_start(self):
        for inventory in self.filtered(lambda x: x.state not in ('done','cancel')):
            vals = {'state': 'confirm', 'date': self.date}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True