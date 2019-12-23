# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime
from odoo.addons import decimal_precision as dp


class non_moving_stock_alshams(models.Model):
    _inherit ='stock.move.line'

    QoH = fields.Float(string='QOH', related = 'product_id.qty_available')

    standard_price = fields.Float(string= 'Cost', related = 'product_id.standard_price')


    company_id = fields.Many2one(string='Company id',
                               related='move_id.company_id')

    num_of_movs = fields.Integer(compute = 'num_of_moves',  default = 0)
    total_price = fields.Float(string = "Total Cost", compute = 'total_cost',  default = 0)

    @api.multi
    def total_cost(self):
        for line in self:
            line.total_price = line.standard_price * line.qty_done




    @api.multi
    def num_of_moves(self):
        num = 0
        list_product = []

        for rec in self:
            if rec.product_id.id not in list_product:
                product_obj = self.env['stock.move.line'].search([('product_id','=',rec.product_id.id),('state','=','done')])
                for line in product_obj:
                    num += 1
                    line.num_of_movs = num
                num = 0
            else:
                list_product.append(rec.product_id.id)


    # def non_moving_function(self):
    #
    #     return {
    #         'name' : 'Filter Moves',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'src_model': 'stock.move.line',
    #         'res_model': 'non.moving.wizard',
    #         'target': 'new',
    #         # 'res_id': self.id,
    #         'context': {'current_id': self.id},
    #         'views': [(self.env.ref('non_moving_stock_alshams.custom_filter_moves_wiz_view').id,'form')],
    #     }

class non_moving_stock_wiz(models.TransientModel):
    _name = 'non.moving.wizard'

    date_from = fields.Datetime(readonly=False)
    date_to = fields.Datetime(readonly=False)
    min_move = fields.Integer(string='Minimum Moves',readonly=False)
    location_id = fields.Many2one('stock.location', 'From')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('non.moving.wizard'),
        index=True)


    def all_filtered_moves(self):
        # moves_obj = self.env['stock.move.line'].search([('date','>',fields.Date.to_string(self.date_from)),('date','<',fields.Date.to_string(self.date_to)),('num_of_movs','<=',self.min_move)])
        nmp_location = []
        moves_id = []
        product_mov_dict = {}
        print (self.date_from,'SSSSSSSSSSSSSSSSSS')
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        date_from = datetime.strptime(str(self.date_from), DATETIME_FORMAT)
        date_to = datetime.strptime(str(self.date_to), DATETIME_FORMAT)
        stock_move_obj = self.env['stock.move'].search([('location_id','=',self.location_id.id), ('company_id','=',self.company_id.id)])
        moves_obj = self.env['stock.move.line'].search([('date','>',date_from),('date','<',date_to),('state','=','done'),('location_id','=',self.location_id.id),('company_id','=',self.company_id.id)])

        for line in stock_move_obj:
            try:
                if len(line.move_line_ids) == 1:
                    moves_id.append(line.move_line_ids.id)
                elif len(line.move_line_ids) > 1:
                    for mv in line.move_line_ids:
                        moves_id.append(mv.id)

            except Exception as e:
                    print( "ERORR", e)




        for line in moves_obj:
            key = str(line.product_id.id)
            if  key in product_mov_dict:
                product_mov_dict[key] +=1
            else:
                product_mov_dict[key] = 1

        product_mov_dict = {key: val for key, val in product_mov_dict.items() if val > self.min_move}


        products_ids = list(product_mov_dict.keys())
        products_ids = [int(x) for x in products_ids]
        moves_obj = self.env['stock.move.line'].search([('product_id', 'in', products_ids), ('id','in',list(moves_obj._ids))])
        print("--------------------------------------")
        print(moves_obj)
        print("--------------------------------------")
        print("--------------------------------------")

        non_moving = set(moves_id) - set(moves_obj._ids)
        moves_obj = self.env['stock.move.line'].search([('id','in',list(non_moving)), ('date','>',date_from),('date','<',date_to)])


        print (moves_obj,'MOOOOOOOOOOVVVVVVV')
        domain = [('id', 'in', moves_obj.ids)]
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', "stock.move.line.tree")])
        # department_id = self.department_id.id)

        return {
            'name': 'Filterd Moves',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.move.line',
            'target': 'current',
            # 'res_id': self.id,
            'context': {'current_id': self.id},
            # 'views': [(self.env.ref('stock.view_move_line_tree').id, 'tree')],
            'views': [(view_id_tree[0].id, 'tree'), (False, 'form')],
            'view_id ref="stock.view_move_line_tree"': '',
            'domain':domain,
        }





