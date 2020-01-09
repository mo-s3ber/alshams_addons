# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from datetime import datetime, date


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    tra_date = fields.Datetime('Transfer Date')

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id

        no_quantities_done = all(float_is_zero(move_line.qty_done,
                                               precision_rounding=move_line.product_uom_id.rounding)
                                 for move_line in self.move_line_ids)

        no_reserved_quantities = all(float_is_zero(move_line.product_qty,
                                                   precision_rounding=move_line.product_uom_id.rounding)
                                     for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_(
                'You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_(
                            'You need to supply a lot/serial number for %s.') % product.display_name)
                    elif line.qty_done == 0:
                        raise UserError(_(
                            'You cannot validate a transfer if you have not processed any quantity for %s.') % product.display_name)

        if not no_quantities_done:
            if not self._check_backorder():
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create(
                    {'pick_ids': [(4, self.id)], 'direct': True})
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
            else:
                return super(stock_picking, self).button_validate()
        else:
            return super(stock_picking, self).button_validate()


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_transfer_price_unit(self, date):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                price_unit = \
                line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id,
                                                                    quantity=1.0)['total_excluded']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                currency = order.currency_id.with_context(date=date)
                price_unit = currency.compute(price_unit, order.company_id.currency_id, round=False)
            return price_unit
        return False

    def _create_account_move_line(self, credit_account_id, debit_account_id,
                                  journal_id):

        if self.purchase_line_id and self.picking_id and self.picking_id.tra_date:
            price = self._get_transfer_price_unit(self.picking_id.tra_date)
            self.write({
                'value': price * self.quantity_done,
                'price_unit': price,
            })

        self.ensure_one()
        AccountMove = self.env['account.move']
        move_lines = self._prepare_account_move_line(self.product_qty,
                                                     abs(self.value),
                                                     credit_account_id,
                                                     debit_account_id)

        if move_lines:
            if self.picking_id.tra_date:
                date_of_transfer = \
                    datetime.strptime(str(self.picking_id.tra_date),
                                      '%Y-%m-%d %H:%M:%S').date()
            else:
                date_of_transfer = date.today()
            new_account_move = AccountMove.create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date_of_transfer,
                'ref': self.picking_id.name,
                'stock_move_id': self.id,
            })
            new_account_move.post()

    remark = fields.Char('Remark')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
