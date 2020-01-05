# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_force_cost = fields.Boolean(string='Force Cost', default=True)


class StockMove(models.Model):
    _inherit = "stock.move"

    is_force_cost = fields.Boolean(string='Force Cost', default=True)

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):

        inventory = self.env['stock.inventory.line'].search([('inventory_id', '=',self.inventory_id.id), ('product_id', '=', self.product_id.id)])
        if inventory:
            if inventory.is_force_cost:
                cost = inventory.force_unit_inventory_cost
            else:
                pass

        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        # # res = set(res)
        # product_ids = {}
        # res_new = []
        # res_force = []
        # for item in res :
        #     if self.is_force_cost :
        #         if item[2]['debit']:
        #             item[2]['debit'] = abs(self.value)
        #
        #         if item[2]['credit']:
        #             item[2]['credit'] = abs(self.value)
        #
        # if self.is_force_cost:
        #     self.price_unit = self.force_unit_inventory_cost
        #
        # for item in res :
        #     if str(item[2]['product_id'])  in product_ids and  product_ids[str(item[2]['product_id'])] < 2:
        #         res_new.append(item)
        #
        #
        #         product_ids[str(item[2]['product_id'])] += 1
        #
        #
        #
        #     elif str(item[2]['product_id'])  not in product_ids :
        #         product_ids[str(item[2]['product_id'])] = 1
        #         res_new.append(item)
        #
        #     else:
        #
        #         pass
        #
        # if self.is_force_cost:
        #     return  res_new
        # else:
        #     for item in res:
        #         if item[2]['debit']:
        #             item[2]['debit'] = abs(item[2]['debit'])
        #
        #         if item[2]['credit']:
        #             item[2]['credit'] = abs(item[2]['credit'])
        return res




    #
    # def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
    #     res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
    #     # res = set(res)
    #     product_ids = {}
    #     for item in res :
    #         if self.is_force_cost and str(item[2]['product_id'])  in product_ids:
    #             # product_ids[str(item[2]['product_id'])] =0
    #
    #             if product_ids[str(item[2]['product_id'])] <= 2 or product_ids['debit' +'_' + str(item[2]['product_id'])] <= 1 \
    #                     or  product_ids['credit' +'_' + str(item[2]['product_id'])] :
    #
    #
    #                 product_ids[str(item[2]['product_id'])] += 1
    #
    #                 if item[2]['debit']:
    #                     item[2]['debit'] = abs(self.value)
    #                     product_ids['debit' +'_' + str(item[2]['product_id'])] = 1
    #
    #                 if item[2]['credit']:
    #                     item[2]['credit'] = abs(self.value)
    #                     product_ids['credit' + '_' + str(item[2]['product_id'])] = 1
    #
    #         else:
    #             product_ids[str(item[2]['product_id'])] = 1
    #
    #     if self.is_force_cost:
    #         self.price_unit = self.force_unit_inventory_cost
    #
    #     return res
