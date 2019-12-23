from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        picking_ids = self.env['stock.picking'].search([('origin', '=', self.name)])
        for pick in picking_ids:
            for stock_move in pick.move_ids_without_package:
                domain = [('picking_id', '=', pick.id), ('product_id', '=', stock_move.product_id.id)]
                move = self.env['stock.move'].search(domain)
                move.product_uom_qty = stock_move.product_uom_qty
                move.move_line_ids[0].product_uom_qty = stock_move.product_uom_qty
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _update_received_qty(self):
        for line in self:
            total = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
                                                                        round=False)
                    else:
                        total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, round=False)
            line.qty_received = total


    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    if inv_line.invoice_id.type == 'in_invoice':
                        qty += inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom, round=False)
                    elif inv_line.invoice_id.type == 'in_refund':
                        qty -= inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom, round=False)
            line.qty_invoiced = qty