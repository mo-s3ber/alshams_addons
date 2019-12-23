# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class inventory_journal_entry_alshams(models.Model):
    _inherit = 'stock.location'

    location_account = fields.Many2one('account.account', string='Location Account', required=False)



# class WareHouseTransientLocation(models.Model):

class inventory_stock_picking(models.Model):
    _inherit = 'stock.picking'

    is_internal_operation = fields.Boolean(compute='_compute_copy_value', default=False,
                                           related='picking_type_id.is_internal_operation')

    @api.onchange('picking_type_id', 'partner_id')
    def _compute_copy_value(self):
        self.is_internal_operation = self.picking_type_id.is_internal_operation

    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document internal")

    # states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},

    origin2 = fields.Many2one('sale.order',
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document outgoing")

    related_operation = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'),('internal', 'Internal')], related = 'picking_type_id.code')

    cheked_transient = fields.Boolean(default= False)
    picking_type_id2 = fields.Many2one('stock.picking.type', string='Destination Operation')

    source_operation = fields.Many2one('stock.picking.type', string='Source Operation', readonly=True)
    source_transfer = fields.Many2one('stock.picking', string='Source Transfer', readonly=True)

    # @api.onchange('picking_type_id')
    # def change_dest_location(self):
    #
    #     self.location_dest_id = self.picking_type_id.default_location_dest_id.id
    #
    #
    # @api.onchange('picking_type_id2')
    # def change_dest_location(self):
    #     self.location_dest_id = self.picking_type_id2.default_location_src_id.id
    #     # if self.picking_type_id.code == 'internal':
    #     #     self.location_dest_id = self.picking_type_id2.default_location_src_id.id
    #     # else:
    #     #     self.location_dest_id = self.picking_type_id.default_location_dest_id.id

    @api.onchange('picking_type_id2', 'partner_id', 'is_internal_operation')
    def onchange_picking_type2(self):
        if self.is_internal_operation and self.picking_type_id2:
            self.location_dest_id = self.picking_type_id2.default_location_src_id.id

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            if self.state == 'draft':
                self.location_id = location_id
                self.location_dest_id = location_dest_id


        # if self.picking_type_id2.code == 'internal':
        #     self.location_dest_id = self.picking_type_id2.default_location_src_id.id
        # TDE CLEANME move into onchange_partner_id
        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in (
                    'no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}

    # @api.depends('picking_type_id2')
    # def change_dest_location(self):
    #
    #     self.location_dest_id = self.picking_type_id2.default_location_src_id.id


    def get_move_vals(self):
        journal_obj = self.env['account.journal'].search(['|', ('name', '=', 'Stock Journal'), ('id', '=', 13)],limit=1)#,'|', ('id', '=', 13)
        return {
            'date': fields.Date.today(),
            # 'partner_id': self.payment_ids[0].partner_id.id,
            'ref':'Internal reference',
            'journal_id': journal_obj.id if journal_obj else 1 ,
        }

    @api.multi
    def button_validate(self):
        res = super(inventory_stock_picking, self).button_validate()
        # print("1",self.move_ids_without_package.mapped('unit_inventory_cost'))
        # raise Warning(self.picking_type_code)


        pick_operation = self.env['stock.picking.type'].browse(self.picking_type_id)
        vendor_and_internal = ['incoming', 'internal']
        # if self.picking_type_id.code in vendor_and_internal and self.cheked_transient is False:
        if self.cheked_transient is False:
            locations_obj = self.env['stock.location'].browse(self.location_id)
            dest_obj = self.env['stock.location'].browse(self.location_dest_id)

        origin1_sale_id = self.env['sale.order'].search([('name', '=', self.origin)],limit=1).id
        origin1_purchase_id = self.env['purchase.order'].search([('name', '=',self.origin)],limit=1).id
        stock_move_obj = self.env['stock.move'].search([('picking_id','=',self.id)])
        for r in stock_move_obj:
            if origin1_purchase_id:
                r.origin1 = origin1_purchase_id
            if origin1_sale_id:
                r.origin2 = origin1_sale_id

        # if self.picking_type_id2.code in vendor_and_internal and self.cheked_transient is False:# and self.origin == '' and self.origin1 is False
        if self.picking_type_id.code == 'internal' and self.cheked_transient is False:# and self.origin == '' and self.origin1 is False
            immidiate_transfer = self.env['stock.immediate.transfer'].create({'pick_ids': [(6, 0, [self.id])]})
            immidiate_transfer.process()
            res = None
            move_package_ids = self.env['stock.move'].search([('id', 'in', self.move_ids_without_package.ids)])
            # move_ids = self.env['stock.move'].search([('id', '=', self.id)])
            # tans_obj = self.env['stock.picking'].browse(self.id)
            # objj = tans_obj
            # print(objj.move_ids_without_package,'objjjjjject')
            # self.env['stock.picking'].create(objj)
            # for t in objj:
            #     print(t.state,'Statttttttttt')
            #     t.state = 'draft'
            #     t.picking_type_id = t.picking_type_id2.id,
            # print("2", self.move_ids_without_package.mapped('unit_inventory_cost'))
            # print(vars(self.move_ids_without_package),'MOVEEEEE')
            transient_obj = {
                'source_operation': self.picking_type_id.id,
                'source_transfer': self.id,
                'origin1': False,
                'origin': '',
                'state': 'assigned',
                'partner_id': self.partner_id.id,
                'scheduled_date': self.scheduled_date,
                # 'analytic_id': self.analytic_id.id,
                'picking_type_id': self.picking_type_id2.id,
                # 'location_id': self.location_dest_id.id,
                # 'location_dest_id':0,

                'location_id': self.picking_type_id2.default_location_src_id.id,
                'location_dest_id': self.picking_type_id2.default_location_dest_id.id,

                # 'location_id': self.location_id.id,
                # 'location_dest_id': self.location_dest_id.id,

                'cheked_transient': True,
                'move_type': self.move_type,
                'company_id': self.company_id.id,
                'show_mark_as_todo': True,
                # 'group_id': self.group_id,
                # 'move_ids_without_package': [(6, 0,self.move_ids_without_package.ids)],
                # 'move_ids_without_package': self.move_ids_without_package.ids,#(6, 0, self.move_ids_without_package.ids) ,#self.move_ids_without_package and
                'move_ids_without_package': [(0, 0,
                                              {'product_id': move_ids_without_package.product_id.id
                                                  , 'product_uom': move_ids_without_package.product_uom.id
                                                  , 'name': move_ids_without_package.name
                                                  , 'location_id': self.picking_type_id2.default_location_src_id.id
                                                  ,
                                               'location_dest_id': self.picking_type_id2.default_location_dest_id.id
                                                  , 'product_uom_qty': move_ids_without_package.product_uom_qty
                                                  , 'quantity_done': move_ids_without_package.quantity_done,
                                               'unit_inventory_cost': abs(
                                                   move_ids_without_package.unit_inventory_cost)}) for
                                             move_ids_without_package in self.move_ids_without_package]
            }
            # print("3", self.move_ids_without_package.mapped('unit_inventory_cost'))

            my_obj = self.env['stock.picking'].create(transient_obj)
            # my_obj.write({'unit_inventory_cost':self.move_ids_without_package.unit_inventory_cost})
            my_obj.action_confirm()
            # my_obj.write({'move_ids_without_package': [(6, 0, self.move_ids_without_package.ids)]})
            # _compute_show_mark_as_todo
            # transient_obj.show_mark_as_todo = True
            # transient_obj.move_ids_without_package = self.move_ids_without_package.ids
            # print(transient_obj.move_ids_without_package, 'Transeeeeeent')
            # print("4", self.move_ids_without_package.mapped('unit_inventory_cost'))

        return res


    # @api.model
    # def create(self, vals):
    #     if vals['origin']:
    #         origin1_sale_id = self.env['sale.order'].search([('name', '=' , vals['origin'])],limit=1).id
    #         origin1_purchase_id = self.env['purchase.order'].search([('name', '=', vals['origin'])],limit=1).id
    #         if origin1_purchase_id:
    #             vals['origin1'] = origin1_purchase_id
    #         if origin1_sale_id:
    #             vals['origin2'] = origin1_sale_id
    #     res = super(inventory_stock_picking, self).create(vals)
    #     return res





class stok_move_custom(models.Model):
    _inherit = 'stock.move'

    origin1 = fields.Many2one('purchase.order',
                              'Source Document', index=True,

                              help="Reference of the document incoming")

    origin2 = fields.Many2one('sale.order',
                              'Source Document', index=True,

                              help="Reference of the document outgoing")

    related_operation = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                                         related='picking_id.picking_type_id.code')


class InternalOperation(models.Model):
    _inherit = 'stock.picking.type'

    is_internal_operation = fields.Boolean(string="Internal", default=False)
