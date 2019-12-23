# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    subcontract_id = fields.Many2one('subcontract.order', related='move_lines.subcontract_line_id.order_id',
        string="Subcontract Orders", readonly=True)

    date_done = fields.Datetime(readonly=False)


class StockMove(models.Model):
    _inherit = 'stock.move'

    subcontract_line_id = fields.Many2one('subcontract.order.line',
        'Subcontract Order Line', ondelete='set null', index=True, readonly=True)
    created_subcontract_line_id = fields.Many2one('subcontract.order.line',
        'Created Subcontract Order Line', ondelete='set null', readonly=True, copy=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields += ['subcontract_line_id', 'created_subcontract_line_id']
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted += [move.subcontract_line_id.id, move.created_subcontract_line_id.id]
        return keys_sorted

    @api.multi
    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.subcontract_line_id and self.product_id.id == self.subcontract_line_id.product_id.id:
            line = self.subcontract_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, self.date, round=False)
            return price_unit
        return super(StockMove, self)._get_price_unit()

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
        """ Overridden from stock_account to support amount_currency on valuation lines generated from po
        """
        self.ensure_one()

        rslt = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id)
        if self.subcontract_line_id:
            subcontract_currency = self.subcontract_line_id.currency_id
            if subcontract_currency != self.company_id.currency_id:
                subcontract_price_unit = self.subcontract_line_id.price_unit
                currency_move_valuation = subcontract_currency.round(subcontract_price_unit * abs(qty))
                rslt['credit_line_vals']['amount_currency'] = rslt['credit_line_vals']['credit'] and -currency_move_valuation or currency_move_valuation
                rslt['credit_line_vals']['currency_id'] = subcontract_currency.id
                rslt['debit_line_vals']['amount_currency'] = rslt['debit_line_vals']['credit'] and -currency_move_valuation or currency_move_valuation
                rslt['debit_line_vals']['currency_id'] = subcontract_currency.id
        return rslt

    def _prepare_extra_move_vals(self, qty):
        vals = super(StockMove, self)._prepare_extra_move_vals(qty)
        vals['subcontract_line_id'] = self.subcontract_line_id.id
        return vals

    def _prepare_move_split_vals(self, uom_qty):
        vals = super(StockMove, self)._prepare_move_split_vals(uom_qty)
        vals['subcontract_line_id'] = self.subcontract_line_id.id
        return vals

    def _clean_merged(self):
        super(StockMove, self)._clean_merged()
        self.write({'created_subcontract_line_id': False})

    def _action_done(self):
        res = super(StockMove, self)._action_done()
        self.mapped('subcontract_line_id').sudo()._update_received_qty()
        return res

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'product_uom_qty' in vals:
            self.filtered(lambda m: m.state == 'done' and m.subcontract_line_id).mapped(
                'subcontract_line_id').sudo()._update_received_qty()
        return res

    def _get_upstream_documents_and_responsibles(self, visited):
        if self.created_subcontract_line_id and self.created_subcontract_line_id.state not in ('done', 'cancel'):
            return [(self.created_subcontract_line_id.order_id, self.created_subcontract_line_id.order_id.user_id, visited)]
        else:
            return super(StockMove, self)._get_upstream_documents_and_responsibles(visited)

    def _get_related_invoices(self):
        """ Overridden to return the vendor bills related to this stock move.
        """
        rslt = super(StockMove, self)._get_related_invoices()
        rslt += self.mapped('picking_id.subcontract_id.invoice_ids').filtered(lambda x: x.state not in ('draft', 'cancel'))
        return rslt


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    buy_to_resupply = fields.Boolean('Buy to Resupply', default=True,
                                     help="When products are bought, they can be delivered to this warehouse")
    buy_pull_id = fields.Many2one('stock.rule', 'Buy rule')

    def _get_global_route_rules_values(self):
        rules = super(StockWarehouse, self)._get_global_route_rules_values()
        location_id = self.in_type_id.default_location_dest_id
        rules.update({
            'buy_pull_id': {
                'depends': ['reception_steps', 'buy_to_resupply'],
                'create_values': {
                    'action': 'buy',
                    'picking_type_id': self.in_type_id.id,
                    'group_propagation_option': 'none',
                    'company_id': self.company_id.id,
                    'route_id': self._find_global_route('subcontract_stock.route_warehouse0_buy', _('Buy')).id
                },
                'update_values': {
                    'active': self.buy_to_resupply,
                    'name': self._format_rulename(location_id, False, 'Buy'),
                    'location_id': location_id.id,
                }
            }
        })
        return rules

    @api.multi
    def _get_all_routes(self):
        routes = super(StockWarehouse, self).get_all_routes_for_wh()
        routes |= self.filtered(lambda self: self.buy_to_resupply and self.buy_pull_id and self.buy_pull_id.route_id).mapped('buy_pull_id').mapped('route_id')
        return routes

    @api.multi
    def _update_name_and_code(self, name=False, code=False):
        res = super(StockWarehouse, self)._update_name_and_code(name, code)
        warehouse = self[0]
        #change the buy stock rule name
        if warehouse.buy_pull_id and name:
            warehouse.buy_pull_id.write({'name': warehouse.buy_pull_id.name.replace(warehouse.name, name, 1)})
        return res


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super(ReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        vals['subcontract_line_id'] = return_line.move_id.subcontract_line_id.id
        return vals


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        for coline in self.env['subcontract.order.line'].search([('state','in',('draft','sent','to approve')),('orderpoint_id','in',self.ids)]):
            res[coline.orderpoint_id.id] += coline.product_uom._compute_quantity(coline.product_qty, coline.orderpoint_id.product_uom, round=False)
        return res

    def action_view_subcontract(self):
        """ This function returns an action that display existing
        subcontract orders of given orderpoint.
        """
        action = self.env.ref('subcontract.subcontract_rfq')
        result = action.read()[0]

        # Remvove the context since the action basically display RFQ and not PO.
        result['context'] = {}
        order_line_ids = self.env['subcontract.order.line'].search([('orderpoint_id', '=', self.id)])
        subcontract_ids = order_line_ids.mapped('order_id')

        result['domain'] = "[('id','in',%s)]" % (subcontract_ids.ids)

        return result


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    subcontract_order_ids = fields.Many2many('subcontract.order', string="Subcontract Orders", compute='_compute_subcontract_order_ids', readonly=True, store=False)
    subcontract_order_count = fields.Integer('Subcontract order count', compute='_compute_subcontract_order_ids')

    @api.depends('name')
    def _compute_subcontract_order_ids(self):
        for lot in self:
            stock_moves = self.env['stock.move.line'].search([
                ('lot_id', '=', lot.id),
                ('state', '=', 'done')
            ]).mapped('move_id').filtered(
                lambda move: move.picking_id.location_id.usage == 'supplier' and move.state == 'done')
            lot.subcontract_order_ids = stock_moves.mapped('subcontract_line_id.order_id')
            lot.subcontract_order_count = len(lot.subcontract_order_ids)

    def action_view_co(self):
        self.ensure_one()
        action = self.env.ref('subcontract.subcontract_form_action').read()[0]
        action['domain'] = [('id', 'in', self.mapped('subcontract_order_ids.id'))]
        return action
