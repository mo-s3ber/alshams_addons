# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class ProductDoneQtyStock(models.Model):
    _inherit = 'stock.move.line'

    done_qty_2 = fields.Float(compute='calculate_qty',digits=dp.get_precision('Product Unit of Measure'))
    my_partner = fields.Many2one('res.partner', compute='calc_partner')
    source_doc = fields.Many2one('purchase.order')

    @api.multi
    def calc_partner(self):
        for re in self:
            re.my_partner = re.picking_id.partner_id.id
            # if re.picking_id.origin1.id:
            #     re.source_doc = re.picking_id.origin1.id

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(ProductDoneQtyStock, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                             orderby=orderby, lazy=lazy)
        accounts = self.env['stock.move.line']
        for line in res:
            if '__domain' in line:
                accounts = self.search(line['__domain'])
            if 'done_qty_2' in fields:
                line['done_qty_2'] = sum(accounts.mapped('done_qty_2'))
        return res

    @api.multi
    def calculate_qty(self, location=False):
        context = self.env.context
        if location == False:

            for rec in self:
                if context.get('location'):
                    print(context.get('location'))
                    if context.get('location') == rec.location_id.id:
                        rec.done_qty_2 = rec.qty_done * -1
                    else:
                        rec.done_qty_2 = rec.qty_done
                else:
                    print("NOT Context")
        else:
            for rec in self:
                if location and location.id == rec.location_id.id:
                    rec.done_qty_2 = rec.qty_done * -1
                elif context.get('location_id'):
                    if context.get('location') == rec.location_id.id:
                        rec.done_qty_2 = rec.qty_done * -1
                    else:
                        rec.done_qty_2 = rec.qty_done
                else:
                    rec.done_qty_2 = rec.qty_done


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    def action_view_stock_moves(self):
        self.ensure_one()
        # context = {'location': self.location_id.id},
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [
            ('product_id', '=', self.product_id.id),
            '|',
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            '|',
                ('package_id', '=', self.package_id.id),
                ('result_package_id', '=', self.package_id.id),
        ]
        action['context'] = {'search_default_done': 1, 'search_default_groupby_product_id': 1,'location': self.location_id.id}
        return action