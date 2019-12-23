# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SubcontractReport(models.Model):
    _inherit = "subcontract.report"

    picking_type_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)

    def _select(self):
        return super(SubcontractReport, self)._select() + ", spt.warehouse_id as picking_type_id"

    def _from(self):
        return super(SubcontractReport, self)._from() + " left join stock_picking_type spt on (spt.id=s.picking_type_id)"

    def _group_by(self):
        return super(SubcontractReport, self)._group_by() + ", spt.warehouse_id"
