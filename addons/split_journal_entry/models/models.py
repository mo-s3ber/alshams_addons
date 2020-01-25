# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import random
import  json
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat
from collections import defaultdict

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_force_cost = fields.Boolean(string='Force Cost', default=True)

class StockMove(models.Model):
    _inherit = 'stock.move'

    serialized_candidates = fields.Char(copy=False,) # used to store price of each item seperately
    unit_inventory_cost = fields.Float("Unit Inventory Cost")
    force_unit_inventory_cost = fields.Float("Unit Inventory Cost")


    # @api.model #override run fifo to fill the serialized_candidates field
    # def _run_fifo(self, move, quantity=None):
    #     """ Value `move` according to the FIFO rule, meaning we consume the
    #     oldest receipt first. Candidates receipts are marked consumed or free
    #     thanks to their `remaining_qty` and `remaining_value` fields.
    #     By definition, `move` should be an outgoing stock move.
    #
    #     :param quantity: quantity to value instead of `move.product_qty`
    #     :returns: valued amount in absolute
    #     """
    #     move.ensure_one()
    #     move.force_unit_inventory_cost = move.unit_inventory_cost
    #
    #     # Deal with possible move lines that do not impact the valuation.
    #     valued_move_lines = move.move_line_ids.filtered(lambda
    #                                                         ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
    #     valued_quantity = 0
    #     for valued_move_line in valued_move_lines:
    #         valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done,
    #                                                                              move.product_id.uom_id)
    #
    #     # Find back incoming stock moves (called candidates here) to value this move.
    #     qty_to_take_on_candidates = quantity or valued_quantity
    #     candidates = move.product_id._get_fifo_candidates_in_move()
    #     new_standard_price = 0
    #     tmp_value = 0  # to accumulate the value taken on the candidates
    #     candidates_data = []
    #     candidates = candidates.filtered(lambda c: c.location_dest_id.id == move.location_id.id)
    #     for candidate in candidates:
    #         new_standard_price = candidate.unit_inventory_cost
    #         if candidate.remaining_qty <= qty_to_take_on_candidates:
    #             qty_taken_on_candidate = candidate.remaining_qty
    #         else:
    #             qty_taken_on_candidate = qty_to_take_on_candidates
    #
    #         # As applying a landed cost do not update the unit price, naivelly  doing
    #         # something like qty_taken_on_candidate * candidate.price_unit won't make
    #         # the additional value brought by the landed cost go away.
    #         candidate_price_unit = candidate.unit_inventory_cost #candidate.remaining_value / candidate.remaining_qty
    #         value_taken_on_candidate = qty_taken_on_candidate * candidate_price_unit
    #         if candidate.unit_inventory_cost!=0:
    #             candidates_data.append({
    #                 'id':candidate.id,
    #                 'qty':qty_taken_on_candidate,
    #                 'price_unit':candidate_price_unit,
    #                 'product_id':candidate.product_id.id,
    #                 'unit_inventory_cost':candidate.unit_inventory_cost
    #             })
    #         else:
    #             candidates_data.append({
    #                 'id': candidate.id,
    #                 'qty': qty_taken_on_candidate,
    #                 'price_unit': candidate_price_unit,
    #                 'product_id': candidate.product_id.id,
    #                 # 'unit_inventory_cost': candidate.unit_inventory_cost
    #             })
    #         candidate_vals = {
    #             'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
    #             'remaining_value': candidate.remaining_value - value_taken_on_candidate,
    #         }
    #         candidate.write(candidate_vals)
    #
    #         qty_to_take_on_candidates -= qty_taken_on_candidate
    #         tmp_value += value_taken_on_candidate
    #         if qty_to_take_on_candidates == 0:
    #             break
    #     if candidates_data:
    #         move.serialized_candidates = json.dumps(candidates_data)
    #     # Update the standard price with the price of the last used candidate, if any.
    #     if new_standard_price and move.product_id.cost_method == 'fifo':
    #         move.product_id.sudo().with_context(force_company=move.company_id.id) \
    #             .standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is called.
        # if qty_to_take_on_candidates == 0:
        #     if (-tmp_value / move.product_qty) !=0:
        #         move.write({
        #             'value': -tmp_value if not quantity else move.value or -tmp_value,
        #         # outgoing move are valued negatively
        #             'price_unit': -tmp_value / move.product_qty,
        #             'unit_inventory_cost': -tmp_value / move.product_qty
        #         })
        #     else:
        #         move.write({
        #             'value': -tmp_value if not quantity else move.value or -tmp_value,
        #             # outgoing move are valued negatively
        #             'price_unit': -tmp_value / move.product_qty,
        #             # 'unit_inventory_cost': -tmp_value / move.product_qty
        #         })
        # elif qty_to_take_on_candidates > 0:
        #     last_fifo_price = new_standard_price or move.product_id.standard_price
        #     negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
        #     tmp_value += abs(negative_stock_value)
        #     if -1 * last_fifo_price!=0:
        #         vals = {
        #             'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
        #             'remaining_value': move.remaining_value + negative_stock_value,
        #             'value': -tmp_value,
        #             'price_unit': -1 * last_fifo_price,
        #             'unit_inventory_cost': -1 * last_fifo_price,
        #         }
        #     else:
        #         vals = {
        #             'remaining_qty': move.remaining_qty + -qty_to_take_on_candidates,
        #             'remaining_value': move.remaining_value + negative_stock_value,
        #             'value': -tmp_value,
        #             'price_unit': -1 * last_fifo_price,
        #             # 'unit_inventory_cost': -1 * last_fifo_price,
        #         }
        #     move.write(vals)
        # if move.unit_inventory_cost == 0:
        #     move.unit_inventory_cost = move.product_id.standard_price
        # return tmp_value

    # def _run_valuation(self, quantity=None):
    #     super(StockMove, self)._run_valuation(quantity=quantity)
    #     if self.force_unit_inventory_cost !=0 or self.unit_inventory_cost != 0:
    #         self.write({
    #             'price_unit': self.force_unit_inventory_cost or self.unit_inventory_cost,
    #         })

    def product_price_update_after_done(self):
        if self.inventory_id:
            if self.inventory_id.force_unit_inventory_cost or self.inventory_id.unit_inventory_cost:
                if self.inventory_id.force_unit_inventory_cost:
                    self.write({
                        'price_unit': self.inventory_id.force_unit_inventory_cost,
                    })
                if self.inventory_id.unit_inventory_cost:
                    self.write({
                        'price_unit': self.inventory_id.unit_inventory_cost,
                    })

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        self.product_price_update_after_done()
        return res

    # def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
    #     # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
    #     self.ensure_one()
    #     rslt = {}
    #     if self._context.get('forced_ref'):
    #         ref = self._context['forced_ref']
    #     else:
    #         ref = self.picking_id.name
    #     if self.serialized_candidates:
    #
    #         for index, item in enumerate(json.loads(self.serialized_candidates)):
    #             debit_line_vals = {
    #                 'name': self.name,
    #                 'product_id': self.product_id.id,
    #                 'quantity': item['qty'],
    #                 'product_uom_id': self.product_id.uom_id.id,
    #                 'ref': ref,
    #                 'partner_id': partner_id,
    #                 'debit': item['qty'] * item['price_unit'], #debit_value if debit_value > 0 else 0,
    #                 'credit': 0,
    #                 'account_id': debit_account_id,
    #             }
    #             credit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': item['qty'],
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': item['qty'] * item['price_unit'],
    #             'debit': 0,
    #             'account_id': credit_account_id,
    #         }
    #             rslt[str(index)+'_debit'] = debit_line_vals
    #             rslt[str(index) + '_credit'] = credit_line_vals
    #     else:
    #         debit_line_vals = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'debit': debit_value if debit_value > 0 else 0,
    #             'credit': -debit_value if debit_value < 0 else 0,
    #             'account_id': debit_account_id,
    #         }
    #         credit_line_vals = {
    #         'name': self.name,
    #         'product_id': self.product_id.id,
    #         'quantity': qty,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'ref': ref,
    #         'partner_id': partner_id,
    #         'credit': credit_value if credit_value > 0 else 0,
    #         'debit': -credit_value if credit_value < 0 else 0,
    #         'account_id': credit_account_id,
    #     }
    #         rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
    #
    #     if credit_value != debit_value:
    #         # for supplier returns of product in average costing method, in anglo saxon mode
    #         diff_amount = debit_value - credit_value
    #         price_diff_account = self.product_id.property_account_creditor_price_difference
    #
    #         if not price_diff_account:
    #             price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
    #         if not price_diff_account:
    #             raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
    #
    #         rslt['price_diff_line_vals'] = {
    #             'name': self.name,
    #             'product_id': self.product_id.id,
    #             'quantity': qty,
    #             'product_uom_id': self.product_id.uom_id.id,
    #             'ref': ref,
    #             'partner_id': partner_id,
    #             'credit': diff_amount > 0 and diff_amount or 0,
    #             'debit': diff_amount < 0 and -diff_amount or 0,
    #             'account_id': price_diff_account.id,
    #         }
    #     return rslt

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

        if self.is_force_cost and self.picking_id.picking_type_id.is_force_cost and self.force_unit_inventory_cost:
            self.value = self.force_unit_inventory_cost * self.quantity_done

        if self.is_force_cost and self.picking_id.picking_type_id.is_force_cost and self.unit_inventory_cost:
            self.value = self.unit_inventory_cost * self.quantity_done

        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            if self.unit_inventory_cost:
                self.value = self.unit_inventory_cost * self.quantity_done
                # self.write({
                #     'value': self.unit_inventory_cost * self.quantity_done,
                # })

        inventory = self.env['stock.inventory.line'].search(
            [('inventory_id', '=', self.inventory_id.id), ('product_id', '=', self.product_id.id)])
        if inventory:
            if inventory.is_force_cost and inventory.force_unit_inventory_cost:
                self.value = inventory.force_unit_inventory_cost * self.quantity_done


        move_lines = self._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            inventory = self.env['stock.inventory.line'].search(
                [('inventory_id', '=', self.inventory_id.id), ('product_id', '=', self.product_id.id)])
            analytic_account_id = False
            if inventory:
                analytic_account_id = inventory.analytic_account_id.id
                ref = self.inventory_id.name
                if self.inventory_id.accounting_date:
                    date = self.inventory_id.accounting_date
            if self.picking_id:
                analytic_account_id = self.picking_id.analytic_id.id

            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': ref,
                'stock_move_id': self.id,
                'analytic_account_id': analytic_account_id,
            })
            new_account_move.post()

    @api.model
    def _get_in_base_domain(self, company_id=False):
        domain = [
            '&',
            '&',
            ('state', '=', 'done'),
            '|',
            ('location_id.company_id', '=', False),
            ('location_id.fifo_candidate_location', '=', True),
            ('location_dest_id.company_id', '=', company_id or self.env.user.company_id.id)
        ]
        return domain

class split_journal_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        if 1 == 2:
            for invoice in self:
                for line_invoice in invoice.invoice_line_ids:
                    if line_invoice.purchase_id:
                        if not line_invoice.purchase_id.user_id.has_group('cash_purchase_shams.group_cash_purchase'):
                            continue
                        stock_moves = line_invoice.purchase_id.picking_ids.mapped("move_ids_without_package").ids

                        post_out_entries = True
                        # raise Warning(line_invoice.purchase_id.picking_ids)
                        for stock_move in stock_moves:
                            # re-calculating
                            out_stock_moves = self.env['stock.move'].search(
                                [('serialized_candidates', 'ilike', '"id": ' + str(stock_move) + ',')])
                            journals = self.env['account.move'].search([('stock_move_id', 'in', out_stock_moves.ids)])
                            # when all moves bills are paid
                            for journal in journals:
                                for line in journal.line_ids:
                                    print("journal_line credit:", line.credit, " debit: ", line.debit)
                                print(
                                    "----------------------------------------------------------------------------------")
                                if journal.state not in ['draft']:
                                    continue
                                in_bills = []
                                out_move = journal.stock_move_id
                                out_move_origins_ids = json.loads(out_move.serialized_candidates)
                                for out in out_move_origins_ids:
                                    # for line in journal.line_ids:
                                    #     print("journal_line credit:", line.credit, " debit: ", line.debit)
                                    # print(
                                    #     "----------------------------------------------------------------------------------")
                                    wh_in = self.env['stock.move'].browse(out['id'])
                                    in_bills.append(wh_in.purchase_line_id.order_id.invoice_ids)
                                    if (wh_in.id == stock_move):
                                        continue
                                    else:
                                        # for line in journal.line_ids:
                                        #     print("journal_line credit:", line.credit, " debit: ", line.debit)
                                        # print(
                                        #     "----------------------------------------------------------------------------------")
                                        # print("wharehouse_id: "+str(wh_in.id))
                                        # print("line_id: "+str(wh_in.purchase_line_id.id))
                                        # print("order_id: "+str(wh_in.purchase_line_id.order_id.id))
                                        # print("invoice_id: "+str(wh_in.purchase_line_id.order_id.invoice_ids.mapped('id')))
                                        if wh_in.purchase_line_id.order_id.invoice_ids.mapped('state') in [False,
                                                                                                           'draft',
                                                                                                           'cancel']:
                                            post_out_entries = False
                                if (post_out_entries):
                                    # for line in journal.line_ids:
                                    #     print("journal_line credit:", line.credit, " debit: ", line.debit)
                                    # print(
                                    #     "----------------------------------------------------------------------------------")
                                    all_invoice_lines = []
                                    for in_bill in in_bills:
                                        for sep_line in in_bill.mapped('invoice_line_ids'):
                                            all_invoice_lines.append(sep_line)
                                    lines_journal_2 = journal.line_ids
                                    for line_invoice_2 in all_invoice_lines:
                                        debit_counter = 0
                                        credit_counter = 0
                                        past_credit = 0.0
                                        past_debit = 0.0
                                        lines_to_remove = []
                                        for line_journal_2 in lines_journal_2:
                                            if int(past_debit) == 0 and int(past_credit) == 0:
                                                print("past_value 0")
                                                if line_journal_2.product_id == line_invoice_2.product_id \
                                                        and credit_counter == 0 \
                                                        and line_invoice_2.product_id.categ_id.property_stock_valuation_account_id == line_journal_2.account_id:
                                                    print("credit: ",
                                                          line_journal_2.quantity * line_invoice_2.unit_inventory_cost)
                                                    past_credit = line_journal_2.with_context(
                                                        check_move_validity=False).credit
                                                    print("past_credit: ", past_credit)
                                                    print("past_debit: ", past_debit)
                                                    line_journal_2.with_context(
                                                        check_move_validity=False).credit = line_journal_2.quantity * line_invoice_2.unit_inventory_cost
                                                    credit_counter += 1
                                                    print("credit_counter: ",
                                                          credit_counter)
                                                    for line in journal.line_ids:
                                                        print("journal_line credit:", line.credit, " debit: ",
                                                              line.debit)
                                                    print(
                                                        "----------------------------------------------------------------------------------")
                                                    lines_to_remove.append(line_journal_2)
                                                elif line_journal_2.product_id == line_invoice_2.product_id \
                                                        and debit_counter == 0 \
                                                        and line_invoice_2.product_id.categ_id.property_stock_account_output_categ_id == line_journal_2.account_id:
                                                    print("debit: ",
                                                          line_journal_2.quantity * line_invoice_2.unit_inventory_cost)
                                                    past_debit = line_journal_2.with_context(
                                                        check_move_validity=False).debit
                                                    print("past_credit: ", past_credit)
                                                    print("past_debit: ", past_debit)
                                                    line_journal_2.with_context(
                                                        check_move_validity=False).debit = line_journal_2.quantity * line_invoice_2.unit_inventory_cost
                                                    debit_counter += 1
                                                    print("debit_counter: ",
                                                          debit_counter)
                                                    for line in journal.line_ids:
                                                        print("journal_line credit:", line.credit, " debit: ",
                                                              line.debit)
                                                    print(
                                                        "----------------------------------------------------------------------------------")
                                                    lines_to_remove.append(line_journal_2)
                                            else:
                                                print("past_value not 0")
                                                if line_journal_2.product_id == line_invoice_2.product_id \
                                                        and credit_counter == 0 \
                                                        and past_debit == line_journal_2.credit \
                                                        and line_invoice_2.product_id.categ_id.property_stock_valuation_account_id == line_journal_2.account_id:
                                                    print("credit: ",
                                                          line_journal_2.quantity * line_invoice_2.unit_inventory_cost)
                                                    past_credit = line_journal_2.with_context(
                                                        check_move_validity=False).credit
                                                    print("past_credit: ", past_credit)
                                                    print("past_debit: ", past_debit)
                                                    line_journal_2.with_context(
                                                        check_move_validity=False).credit = line_journal_2.quantity * line_invoice_2.unit_inventory_cost
                                                    credit_counter += 1
                                                    print("credit_counter: ",
                                                          credit_counter)
                                                    for line in journal.line_ids:
                                                        print("journal_line credit:", line.credit, " debit: ",
                                                              line.debit)
                                                    print(
                                                        "----------------------------------------------------------------------------------")
                                                    lines_to_remove.append(line_journal_2)
                                                elif line_journal_2.product_id == line_invoice_2.product_id \
                                                        and debit_counter == 0 and past_credit == line_journal_2.debit \
                                                        and line_invoice_2.product_id.categ_id.property_stock_account_output_categ_id == line_journal_2.account_id:
                                                    print("debit: ",
                                                          line_journal_2.quantity * line_invoice_2.unit_inventory_cost)
                                                    past_debit = line_journal_2.with_context(
                                                        check_move_validity=False).debit
                                                    print("past_credit: ", past_credit)
                                                    print("past_debit: ", past_debit)
                                                    line_journal_2.with_context(
                                                        check_move_validity=False).debit = line_journal_2.quantity * line_invoice_2.unit_inventory_cost
                                                    debit_counter += 1
                                                    print("debit_counter: ",
                                                          debit_counter)
                                                    for line in journal.line_ids:
                                                        print("journal_line credit:", line.credit, " debit: ",
                                                              line.debit)
                                                    print(
                                                        "----------------------------------------------------------------------------------")
                                                    lines_to_remove.append(line_journal_2)
                                            if past_credit == past_debit:
                                                past_credit = 0.0
                                                past_debit = 0.0

                                        for item in lines_to_remove:
                                            lines_journal_2 = lines_journal_2.filtered(lambda r: r.id != item.id)
                                    # for line in journal.line_ids:
                                    #     if line.debit != line.credit:
                                    #         line.with_context(check_move_validity=False).debit = line.credit
                                    #     print("journal_line credit:",line.credit," debit: ",line.debit)
                                    # journal.post()

                                    # posting out moves

                        stock_moves = line_invoice.purchase_id.picking_ids.mapped("move_ids_without_package").filtered(
                            lambda r: r.product_id == line_invoice.product_id).ids
                        journals = self.env['account.move'].search([('stock_move_id', 'in', stock_moves)])
                        for journal in journals:
                            if journal.state == "posted":
                                continue
                            for line_journal in journal.line_ids:
                                if line_invoice.account_id == line_journal.account_id:
                                    print('AAAAAAE', line_invoice.account_analytic_id.id, 'DDDDD',
                                          line_journal.analytic_account_id)
                                    # line_journal.analytic_account_id = line_invoice.account_analytic_id.id
                                    line_journal.with_context(
                                        check_move_validity=False).credit = line_journal.quantity * line_invoice.unit_inventory_cost
                                elif line_invoice.product_id.categ_id.property_stock_valuation_account_id == line_journal.account_id:
                                    line_journal.with_context(
                                        check_move_validity=False).debit = line_journal.quantity * line_invoice.unit_inventory_cost
                                    # line_journal.analytic_account_id = line_invoice.account_analytic_id.id
                            journal.post()
                            # posting in moves
            stock_moves = line_invoice.purchase_id.picking_ids.mapped("move_ids_without_package").ids
            for stock_move in stock_moves:
                out_stock_moves = self.env['stock.move'].search(
                    [('serialized_candidates', 'ilike', '"id": ' + str(stock_move) + ',')])
                journals = self.env['account.move'].search([('stock_move_id', 'in', out_stock_moves.ids)])

                for journal in journals:
                    journal.post()
                # for journal in journals:
                #     try:
                #
                #         journal.post()
                #         print(journal.id)
                #     except Exception as e:
                #         print(e)
                #         print('erorr', journal.id)
            res = super(split_journal_invoice, self).action_invoice_open()
            if not self:
                return res
            return res
        return super(split_journal_invoice, self).action_invoice_open()

class split_journal_stock_location(models.Model):
    _inherit = 'stock.location'
    fifo_candidate_location = fields.Boolean('FIFO Candidate Location')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            if tax_line.amount_total:
                tax = tax_line.tax_id
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)

                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in tax_line.analytic_tag_ids]
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': tax_line.amount_total,
                    'quantity': 1,
                    'price': tax_line.amount_total,
                    'account_id': tax_line.account_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'invoice_id': self.id,
                    'product_id': tax_line.product_id.id,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res

    # @api.model
    # def tax_line_move_line_get(self):
    #     res = super(add_product_in_account_invoice_tax_line,self).tax_line_move_line_get()
    #     dict = {}
    #     for line in self.invoice_line_ids:
    #         for tax in self.tax_line_ids:
    #             for tx_line in res:
    #                 if str(tax.id) not in dict:
    #                     dict[str(tax.id)] = []
    #                 similiar_tax_lines = self.tax_line_ids.filtered(lambda tx: tx.id != tax.id and tax.tax_id.id == tx.tax_id.id )
    #                 flag_break = False
    #                 for simi_line in similiar_tax_lines:
    #                     if str(simi_line.id) in dict:
    #                         if line.id in dict[str(simi_line.id)]:
    #                             flag_break = True
    #                 if flag_break:
    #                     continue
    #                 if len(dict[str(tax.id)]) < 1 and tx_line['invoice_tax_line_id'] == tax.id:
    #                     tx_line['product_id'] = line.product_id.id
    #                     dict[str(tax.id)].append(line.id)
    #     return res

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            if not line.account_id:
                continue
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val) + "_" + str(line.id)
                tax_grouped[key] = val
                # if key not in tax_grouped:
                #     tax_grouped[key] = val
                # else:
                    # key += str(random.randint(-10100,10100))
                    # tax_grouped[key] = val
        return tax_grouped

    def _prepare_tax_line_vals(self, line, tax):
        res = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        res['product_id'] = line.product_id.id
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    product_id = fields.Many2one('product.product', 'Product')



class StockInventory(models.Model):
    _inherit="stock.inventory"

    def _action_done(self):
        negative = next((line for line in self.mapped('line_ids') if
                         line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
        if negative:
            raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (
            negative.product_id.name, negative.product_qty))
        self.action_check()
        for move in self.mapped('move_ids'):
            move._run_fifo(move)
        self.write({'state': 'done'})
        self.post_inventory()
        return True

    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
