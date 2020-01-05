# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from itertools import groupby
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     internal_transfer_account_id = fields.Many2one('account.account', string="Account")
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSettings, self).get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         guarantee = params.get_param('internal_transfer_account_id')
#
#         res.update(
#             internal_transfer_account_id=guarantee and int(guarantee) or '',
#         )
#         return res
#
#     @api.multi
#     def set_values(self):
#         res = super(ResConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param('internal_transfer_account_id',
#                                                          self.internal_transfer_account_id and
#                                                          self.internal_transfer_account_id.id or '')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # @api.multi
    # def button_validate(self):
    #     self.ensure_one()
    #     if not self.move_lines and not self.move_line_ids:
    #         raise UserError(_('Please add some items to move.'))
    #
    #     # If no lots when needed, raise error
    #     picking_type = self.picking_type_id
    #     precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
    #     no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
    #     if no_reserved_quantities and no_quantities_done:
    #         raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))
    #
    #     if picking_type.use_create_lots or picking_type.use_existing_lots:
    #         lines_to_check = self.move_line_ids
    #         if not no_quantities_done:
    #             lines_to_check = lines_to_check.filtered(
    #                 lambda line: float_compare(line.qty_done, 0,
    #                                            precision_rounding=line.product_uom_id.rounding)
    #             )
    #
    #         for line in lines_to_check:
    #             product = line.product_id
    #             if product and product.tracking != 'none':
    #                 if not line.lot_name and not line.lot_id:
    #                     raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)
    #
    #     if no_quantities_done:
    #         view = self.env.ref('stock.view_immediate_transfer')
    #         wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
    #         return {
    #             'name': _('Immediate Transfer?'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'stock.immediate.transfer',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }
    #
    #     if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
    #         view = self.env.ref('stock.view_overprocessed_transfer')
    #         wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'stock.overprocessed.transfer',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }
    #
    #     # Check backorder should check for other barcodes
    #     if self._check_backorder():
    #         return self.action_generate_backorder_wizard()
    #     self.action_done()
    #     internal_transfer_account_id = int(
    #         self.env['ir.config_parameter'].sudo().get_param('internal_transfer_account_id'))
    #
    #     if not internal_transfer_account_id:
    #         raise UserError('Please Select Internal Transfer Account in configuration')
    #     else:
    #         account_debit = int(internal_transfer_account_id)
    #
    #     if self.location_id.usage == 'transit' and self.picking_type_id.code == 'internal':
    #         for line in self.move_ids_without_package:
    #             self.move(line.product_id.categ_id.property_stock_journal.id,
    #                       line.unit_inventory_cost * line.quantity_done, account_debit,
    #                       line.product_id.categ_id.property_stock_valuation_account_id.id, self.name)
    #     if self.location_dest_id.usage == 'transit' and self.picking_type_id.code == 'internal':
    #         if self.move_ids_without_package:
    #             for line in self.move_ids_without_package:
    #                 self.move(line.product_id.categ_id.property_stock_journal.id,
    #                           line.unit_inventory_cost * line.quantity_done,
    #                           line.product_id.categ_id.property_stock_valuation_account_id.id, account_debit, self.name)
    #
    #     return

    # @api.multi
    # def action_confirm(self):
    #     internal_transfer_account_id = int(self.env['ir.config_parameter'].sudo().get_param('internal_transfer_account_id'))
    #
    #     if not internal_transfer_account_id:
    #         raise UserError('Please Select Internal Transfer Account in configuration')
    #     else:
    #         account_debit = int(internal_transfer_account_id)
    #
    #     if self.location_id.usage == 'transit' and self.picking_type_id.code == 'internal':
    #         for line in self.move_ids_without_package:
    #             self.move(line.product_id.categ_id.property_stock_journal.id,
    #                       line.unit_inventory_cost * line.quantity_done, account_debit,
    #                       line.product_id.categ_id.property_stock_valuation_account_id.id, self.name)
    #     if self.location_dest_id.usage == 'transit' and self.picking_type_id.code == 'internal':
    #         if self.move_ids_without_package:
    #             for line in self.move_ids_without_package:
    #                 self.move(line.product_id.categ_id.property_stock_journal.id,
    #                           line.unit_inventory_cost * line.quantity_done,
    #                           line.product_id.categ_id.property_stock_valuation_account_id.id, account_debit, self.name)
    #
    #     self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
    #     # call `_action_confirm` on every draft move
    #     self.mapped('move_lines') \
    #         .filtered(lambda move: move.state == 'draft') \
    #         ._action_confirm()
    #     # call `_action_assign` on every confirmed move which location_id bypasses the reservation
    #     self.filtered(lambda picking: picking.location_id.usage in (
    #         'supplier', 'inventory', 'production') and picking.state == 'confirmed') \
    #         .mapped('move_lines')._action_assign()
    #     return True

    def move(self, journal_id, amount, account_credit, account_debit, name):
        lines = [
            (0, 0, {
                'name': str(name),
                'account_id': account_credit,
                'debit': 0,
                'credit': amount,
                'partner_id': self.partner_id.id,
                'date_maturity': fields.Date.today(),

            }),
            (0, 0, {
                'name': '/',
                'account_id': account_debit,
                'debit': amount,
                'credit': 0,
                'partner_id': self.partner_id.id,
                'date_maturity': fields.Date.today(),
            })
        ]
        move_id = self.env['account.move'].create({
            'date': fields.Date.today(),
            'journal_id': journal_id,
            'ref': name,
            'line_ids': lines,
            'analytic_account_id': self.analytic_id.id,

        })
        move_id.post()


class AccountMove(models.Model):
    _inherit = 'account.move'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('analytic_account_id')
    @api.constrains('analytic_account_id')
    def set_analytic_account_lines(self):
        for record in self:
            if record.line_ids:
                for line in record.line_ids:
                    line.analytic_account_id = record.analytic_account_id


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    is_force_cost = fields.Boolean(string='Force Cost', default=True, copy=False)
    force_unit_inventory_cost = fields.Float("Unit Inventory Cost")


class StockMove(models.Model):
    _inherit = "stock.move"

    is_force_cost = fields.Boolean(string='Force Cost', default=True)

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value),
                                                                                  credit_account_id, debit_account_id)
        analytic_account_id = 0
        if move_lines:
            inventory = self.env['stock.inventory.line'].search(
                [('inventory_id', '=', self.inventory_id.id), ('product_id', '=', self.product_id.id)])
            if inventory:
                analytic_account_id = inventory.analytic_account_id.id
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
                'analytic_account_id': analytic_account_id
            })
            new_account_move.post()

    # def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
    #     """
    #     Generate the account.move.line values to post to track the stock valuation difference due to the
    #     processing of the given quant.
    #     """
    #     self.ensure_one()
    #
    #     if self._context.get('force_valuation_amount'):
    #         valuation_amount = self._context.get('force_valuation_amount')
    #     else:
    #         valuation_amount = cost
    #
    #     inventory = self.env['stock.inventory.line'].search(
    #         [('inventory_id', '=', self.inventory_id.id), ('product_id', '=', self.product_id.id)])
    #     print('*******************')
    #     if inventory:
    #         if inventory.is_force_cost:
    #             valuation_amount = inventory.force_unit_inventory_cost * qty
    #     # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
    #     # the company currency... so we need to use round() before creating the accounting entries.
    #     debit_value = self.company_id.currency_id.round(valuation_amount)
    #
    #     # check that all data is correct
    #     if self.company_id.currency_id.is_zero(debit_value):
    #         raise UserError(_(
    #             "The cost of %s is currently equal to 0. Change the cost or the configuration of your product to avoid an incorrect valuation.") % (
    #                             self.product_id.display_name,))
    #     credit_value = debit_value
    #
    #     valuation_partner_id = self._get_partner_id_for_valuation_lines()
    #     res = [(0, 0, line_vals) for line_vals in
    #            self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value,
    #                                                debit_account_id, credit_account_id).values()]
    #
    #     return res
