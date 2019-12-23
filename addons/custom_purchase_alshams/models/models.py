# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class custom_internal_seq(models.Model):
    _inherit = "product.category"

    code = fields.Char()

# options="{'no_create_edit': True, 'no_quick_create': True}"

class custom_purchase_alshams(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True)#give default value

    _sql_constraints = [
        ('code_default_code_uniq', 'unique (default_code)', 'Internal reference should be unique !')
    ]

    # @api.model
    # def create(self, vals):
    #     # vals['default_code'] = self.env['ir.sequence'].next_by_code('product.template')
    #     seq = self.env['ir.sequence'].get('product.template') or '/'
    #     seq = seq.replace('DEGREE', str(self.categ_id.code))
    #     print (str(self.categ_id.code),'LLLLLLLL')
    #     vals['default_code'] = seq
    #     return super(custom_purchase_alshams, self).create(vals)

    @api.model
    def create(self, vals):
        category = self.env['product.category'].search([('id', '=', vals['categ_id'])])
        seq = self.env['ir.sequence'].next_by_code('product.template') or '/'
        seq = seq.replace('CODE', str(category.code))
        vals['default_code'] = seq
        return super(custom_purchase_alshams, self).create(vals)


    @api.multi
    def write(self, vals):
        res = super(custom_purchase_alshams, self).write(vals)
        # if self.state == 'posted':
        if 'categ_id' in vals:
            print (vals['categ_id'],'SSSSSSSSSSSS')
            category = self.env['product.category'].search([('id','=',vals['categ_id'])])
            print (category,'CCCCCCCCAT')
            seq = self.env['ir.sequence'].get('product.template') or '/'
            seq = seq.replace('CODE', str(category.code))
            print (seq,'SSSSSSQQQQQ')
            vals['default_code'] = seq
            self.default_code = seq
            print (vals['default_code'],'GGGGGGG',self.default_code)
        return res

    # @api.onchange('categ_id')
    # def generate_seq(self):
    #
        # seq = self.env['ir.sequence'].get('product.template') or '/'
        # seq = seq.replace('CODE', str(self.categ_id.code))
        # print (str(self.categ_id.code), 'LLLLLLLL')
        # self.default_code = seq



class custom_res_partner_code(models.Model):
    _inherit = 'res.partner'


    tax_file = fields.Char()
    tax_department = fields.Char()
    national_id = fields.Char()


    @api.model
    def create(self, vals):
        # vals['default_code'] = self.env['ir.sequence'].next_by_code('product.template')
        seq = self.env['ir.sequence'].get('res.partner') or '/'
        vals['ref'] = seq
        return super(custom_res_partner_code, self).create(vals)


class custom_purchase_order(models.Model):
    _inherit = 'purchase.order'
    submitted_person = fields.Many2one('res.users')
    approved_person = fields.Many2one('res.users')
    confirmed_person = fields.Many2one('res.users')

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('wait', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def action_submit(self):
        self.submitted_person = self.env.user.id
        # print(self.submitted_person,'SSSSSSSSSSSSSSSB')
        return self.write({
            'state': 'wait',
        })

    @api.multi
    def action_approve(self):
        if self.env.user.has_group('custom_purchase_alshams.group_purchase_approval_alshanas'):
            self.approved_person = self.env.user.id
            return self.write({
                'state': 'approved',
            })
        else:
            raise UserError("You don't have permission to approve")


    @api.multi
    def button_confirm(self):
        for order in self:
            self.confirmed_person = self.env.user.id
            if order.state not in ['draft', 'sent','approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
