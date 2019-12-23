# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import RedirectWarning, UserError, ValidationError

# from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)




class journal_entry_inheriy(models.Model):
    _inherit = 'account.move'

    journal_parent = fields.Many2one('account.batch.deposit', string="Journal parent")


class cheque(models.Model):
    _inherit = 'account.payment'

    cheque_hash = fields.Char("Cheque #")
    cheque_date = fields.Date("Maturity Date", default=fields.Date.today())
    account = fields.Many2one('account.account', string="Bank Account")
    pruchase_deposit = fields.Many2one('pruchase.deposit.edit')
    name_of_journal = fields.Char(related='journal_id.name')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'),('matched','Matched'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")

    # partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')],compute='_compute_partner_type')

    # @api.depends('batch_deposit_id.cheque_type')
    # def _compute_partner_type(self):
    #         if self.batch_deposit_id.cheque_type =='in':
    #             self.partner_type='customer'
    #         if self.batch_deposit_id.cheque_type =='out':
    #             self.partner_type = 'supplier'

    # @api.model
    # def create(self, vals):
    #     result = super(cheque, self).create(vals)
    #     if self.batch_deposit_id.cheque_type == 'in':
    #         self.partner_type = 'customer'
    #     if self.batch_deposit_id.cheque_type == 'out':
    #         self.partner_type = 'supplier'
    #
    #
    #     return result


    @api.multi
    def write(self, vals):
        result = super(cheque, self).write(vals)
        if 'journal_id' in vals:
            for team in self:
                match_payment = team.env['account.move.line'].search([('payment_id', '=', team.id)],limit=1)
                match_payment.move_id.button_cancel()
                match_payment.update({'account_id': team.journal_id.default_debit_account_id})

        if 'state' in vals:
            if vals['state']=='matched':
                if self.batch_deposit_id:
                    if self.batch_deposit_id.cheque_type == 'out':
                        self.batch_deposit_id.state_out = 'matched'

                    elif self.batch_deposit_id.cheque_type == 'in':
                        self.batch_deposit_id.state_in = 'matched'
        # print(self, vals, result)
        # self.hide_payment_method = False

        return result



class AddAccounts(models.Model):
    _inherit = 'account.batch.deposit'


    journal_id = fields.Many2one('account.journal', string='Bank', domain=[('type', '=', 'bank')], required=True,
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self._get_default_journal())

    @api.model
    def _get_default_journal(self):
        print(self.cheque_type)
        if self.cheque_type == 'out':
            return
        IrDefault = self.env['ir.default'].sudo()
        cheque_draft_journal_id = IrDefault.get(
            'account.batch.deposit', 'cheque_draft_journal_id', company_id=self.env.user.company_id.id)

        if not cheque_draft_journal_id:
            raise ValidationError("Please Choose Journal In Settings")
        print(cheque_draft_journal_id)
        return cheque_draft_journal_id

    # @api.model
    # def create(self, vals):
    #     if not vals.get('name'):
    #         journal_id = vals['journal_id']
    #         # journal_id = vals.get('journal_id', self.env.context.get('default_journal_id', False))
    #         # journal = self.env['account.journal'].browse(journal_id)
    #         vals['name'] = journal_id.batch_deposit_sequence_id.with_context(
    #             ir_sequence_date=vals.get('date')).next_by_id()
    #     rec = super(AddAccounts, self).create(vals)
    #     rec.normalize_payments()
    #     return rec

    @api.one
    @api.constrains('payment_ids', 'cheque_type')
    def _check_cheque_type_partner_type(self):
        if self.cheque_type == 'out':
            for payment in self.payment_ids:
                if payment.partner_type == 'customer':
                    raise ValidationError("if the cheque type is out you have to choose vendor not customer")


    state_in = fields.Selection([('draft', 'Draft'),
         ('cheques_in_safe', 'Cheque In Safe'),
         ('cheques_under_collection', 'Cheque Under Collection'),
         ('collect', 'Collect'),
         ('reject', 'Reject'),
         ('matched', 'Matched'),

     ],
         string='Status',
         readonly=True,
          default='draft',
     )

    state_out = fields.Selection([('draft', 'Draft'),
                                 ('to_pay', 'To pay'),
                                 ('close', 'Close'),
                                 ('matched', 'Matched')

                                 ],
                                string='Status',
                                readonly=True,
                                default='draft',
                                )

    journal_entry_ids = fields.One2many(
        'account.move',
        'journal_parent',
        string="Journal entries"
    )
    payements_ids = fields.One2many(
        'account.payment',
        'batch_deposit_id',
        string="payments"
    )

    journal_entry_number = fields.Integer(
        compute='_compute_journal_entry_amount_total',
        string="journal entry number"
    )
    payements_number = fields.Integer(
        compute='_compute_payments_amount_total',
        string="payments number"
    )

    
    account_id_receipt_intermediate = fields.Many2one('account.account')

    account_id_transfer_intermediate = fields.Many2one('account.account')

    account_id_receipt_intermediate_out = fields.Many2one('account.account')
    # intermediate_account_out = fields.Many2one('account.account')

    account_id_transfer_intermediate_out = fields.Many2one('account.account')

    cheque_draft_journal_id = fields.Many2one('account.journal')


    cheque_number = fields.Char("Cheque Number")
    account_1 = fields.Many2one('account.account', string="Account 1")
    account_2 = fields.Many2one('account.account', string="Bank Account")
    rec_account_1 = fields.Many2one(
        'account.account', string="Recieve Debit Account")
    rec_account_2 = fields.Many2one(
        'account.account', string="Recieve Credit Account")
    pay_debit_setting = fields.Many2one(
        'account.account', string="Pay Debit Account")

    pay_credit_setting = fields.Many2one(
        'account.account', string="Pay Credit Account")

    maturity_date = fields.Date("Maturity Date")
    state_of_cheque = fields.Selection([
        ('cheque_under_collection', 'Cheque Under Collection'),
        ('cheque_in_bank', 'Cheque In Bank'),
        ('collection', 'Collection'),
        ('reject', 'Rejected')
    ],
        string='Status',
        readonly=True,
        # default='cheque_under_collection',
    )
    cheque_type = fields.Selection(
        [('in', 'IN'), ('out', 'OUT')],
        required=True,
        default='in'
    )
    state_of_cheque2 = fields.Selection(
        [
            ('to_client', 'To Client'),
            ('close', 'Close'),
            ('reject', 'Rejected')
        ],
        string='Status 2',
        readonly=True,
        # default='to_client',
    )

    partner_id = fields.Char(compute='_compute_partner_id')
    current_state_of_cheque = fields.Char(compute='_compute_state_of_cheque')

    move_name = fields.Char(string='Journal Entry Name', readonly=True,
                            default=False, copy=False)
    date_to = fields.Datetime('Retrieving Date')
    status_date = fields.Datetime('Status Date')
    state_json = fields.Char('States JSON')

    @api.one
    @api.constrains('journal_id', 'payment_ids')
    def _check_same_journal(self):
        pass

    # @api.one
    # def normalize_payments(self):
    #     # Make sure all payments have batch_deposit as payment method (a payment created via the form view of the
    #     # payment_ids many2many of the batch deposit form view cannot receive a default_payment_method in context)
    #     self.payment_ids.write(
    #         {'payment_method_id': self.env.ref('account_batch_deposit.account_payment_method_batch_deposit').id})
    #     # Since a batch deposit has no confirmation step (it can be used to select payments in a bank reconciliation
    #     # as long as state != reconciled), its payments need to be posted
    #     self.payment_ids.filtered(lambda r: r.state == 'draft').post()

    # @api.multi
    # def write(self, vals):
    #     result = super(AddAccounts, self).write(vals)
    #     # if 'journal_id' in vals:
    #     #     for team in self:
    #     #         match_payment = team.env['account.payment'].search([('batch_deposit_id', '=', team.id)])
    #     #
    #     #         match_payment.update({'journal_id': team.journal_id})
    #
    #     return result



    @api.depends('journal_entry_ids')
    def _compute_journal_entry_amount_total(self):
        for i in self:
            nbr = 0
            for j in i.journal_entry_ids:
                nbr += 1
            i.journal_entry_number = nbr

    @api.depends('payements_ids')
    def _compute_payments_amount_total(self):
        for i in self:
            nbr = 0
            for j in i.payements_ids:
                nbr += 1
            i.payements_number = nbr

    @api.one
    @api.depends('date_to','state_in','state_out','state_of_cheque', 'state_of_cheque2')
    def _compute_state_of_cheque(self):
        # print("::: _compute_state_of_cheque ::::")
        current = False
        json = False
        # if(self.state_of_cheque):
        if self.cheque_type == 'in':
            current = dict(self._fields['state_in'].selection).get(self.state_in)
            # current = self.state_of_cheque
            # self.current_state_of_cheque = current
        else:
            current = dict(self._fields['state_out'].selection).get(self.state_out)
            #current = #self.state_of_cheque2
            # self.current_state_of_cheque = current
        # print(current)
        # print(self.state_json)
        if current:
            if self.state_json:
                json = eval(self.state_json)
                json[current] = self.status_date
                self.state_json = str(json)
            else:
                json = {current: self.status_date}
                self.state_json = str(json)
        # print(json)
        # print(self.date_to)
        if self.date_to and json and current:
            # print('::::  Iam IN ::::')
            for key, value in json.items():
                date_1 = fields.Datetime.from_string(str(value))
                date_2 = fields.Datetime.from_string(str(self.date_to))
                if date_1 > date_2:
                    current = key
                    break
        # print(current)
        print(current, self.state_json)
        self.current_state_of_cheque = current

    @api.one
    @api.depends('payment_ids')
    def _compute_partner_id(self):
        if(self.payment_ids):
            self.partner_id = self.payment_ids[0].partner_id.name

    @api.one
    def transfer_collect(self):
        # print(':::: NEXT ::::')
        if self.state_in == 'cheques_in_safe':
            IrDefault = self.env['ir.default'].sudo()
            cheque_draft_journal_id = IrDefault.get(
                'account.batch.deposit', 'cheque_draft_journal_id', company_id=self.env.user.company_id.id)
            print("settings journal ",self.cheque_draft_journal_id.id, cheque_draft_journal_id)
            if self.journal_id.id == cheque_draft_journal_id:
                raise ValidationError("Can't Transfer to bank. Please Change the Journal.")
            # print('cheque_under_collection')
            self.create_journal_entry()
            self.state_in = 'cheques_under_collection'

        elif self.state_in == 'cheques_under_collection':
            # print('cheque_in_bank')
            self.create_journal_entry2()
            self.state_in = 'collect'
        return True

    @api.one
    def recieve(self):
        # # print(':::: Recieve  :::::')
        # aml_obj = self.env['account.move.line'].with_context(
        #     check_move_validity=False)
        # # print(aml_obj)
        # account_values ={
        #     'date':self.date,
        #     'ref':self.cheque_number,
        #     'journal_id':self.journal_id.id,
        #     'journal_parent':self.id
        # }
        # move = self.env['account.move'].create(account_values)
        # IrDefault = self.env['ir.default'].sudo()
        #
        # rec_account_1 = IrDefault.get(
        #     'account.batch.deposit', 'rec_account_1', company_id=self.env.user.company_id.id)
        # rec_account_2 = IrDefault.get(
        #     'account.batch.deposit', 'rec_account_2', company_id=self.env.user.company_id.id)
        #
        # # print(move)
        # values = {
        #     'account_id': rec_account_2,
        #     'name': move.ref,
        #     'move_id': move.id,
        #     'partner_id': self.payment_ids[0].partner_id.id,
        #     'help': 'a',
        #     'credit': self.amount,
        #     'date_maturity': fields.Date.today(),
        # }
        # aml_obj.create(values)
        # values = {
        #     'account_id': rec_account_1,
        #     'name': move.ref,
        #     'move_id': move.id,
        #     'partner_id': self.payment_ids[0].partner_id.id,
        #     'help': 'a',
        #     'debit': self.amount,
        #     'date_maturity': fields.Date.today(),
        # }
        # aml_obj.create(values)
        # move.post()
        # self.move_name = move.name
        # self.write({'journal_id': False})
        self.write({'state_in': 'cheques_in_safe'})
        self.payment_ids.filtered(lambda r: r.state == 'draft').post()



    def create_journal_entry(self):
        print(':::  create_journal_entry :::')
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        account_values = {
            'date': self.date,
            'ref': self.cheque_number,
            'journal_id': self.journal_id.id,
            'journal_parent': self.id

        }
        move = self.env['account.move'].create(account_values)
        print("themooooooooooove",move)
        if self.state_in == 'cheques_in_safe':


            IrDefault = self.env['ir.default'].sudo()
            #ICPSudo = self.env['ir.config_parameter'].sudo()
            intermediate_account = IrDefault.get(
                'account.batch.deposit','account_id_receipt_intermediate', company_id=self.env.user.company_id.id)
            transfer_account = IrDefault.get(
                'account.batch.deposit','account_id_transfer_intermediate', company_id=self.env.user.company_id.id)



            #account_1 = self.env["ir.config_parameter"].sudo().get_param(
            #    'payement_cheque.intermediate_account',)
            # debit = self.amount
            # credit = self.amount
            values = {
                'account_id': intermediate_account,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            #account_1 = self.env["ir.config_parameter"].sudo().get_param(
            #    'payement_cheque.transfer_account',)
            values = {
                'account_id': transfer_account,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
        # move.post()
        if self.move_name:
            self.move_name = self.move_name + ' ' + move.name
        else:
            self.move_name = move.name

    def create_journal_entry2(self):
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        move = self.env['account.move'].search([('date', '=',self.date),('ref','=',self.cheque_number),('journal_id','=',self.journal_id.id),('journal_parent','=',self.id)],limit=1)
        if self.state_in == 'cheques_under_collection':
            IrDefault = self.env['ir.default'].sudo()
            #ICPSudo = self.env['ir.config_parameter'].sudo()
            intermediate_account = IrDefault.get(
                'account.batch.deposit','account_id_receipt_intermediate', company_id= self.env.user.company_id.id)
            transfer_account = IrDefault.get(
                'account.batch.deposit','account_id_transfer_intermediate', company_id= self.env.user.company_id.id)

            #account_1 = self.env["ir.config_parameter"].sudo().get_param(
            #    'payement_cheque.transfer_account',)
            # credit = self.amount
            values = {
                'account_id': transfer_account,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            values = {
                'account_id': self.journal_id.default_debit_account_id.id,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
        # move.post()

    def get_move_vals(self):
        return {
            'date': fields.Date.today(),
            'partner_id': self.payment_ids[0].partner_id.id,
            'ref': self.payment_ids[0].communication,
            'journal_id': self.journal_id.id,
        }

    @api.one
    def next_out(self):
        self.create_out_row()
        self.state_of_cheque2 = 'close'

        return

    def create_out_row(self):
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        values = self.get_move_vals()
        move = self.env['account.move'].create(values)
        values = {
            'account_id': self.account_2.id,
            'name': move.ref,
            'move_id': move.id,
            'partner_id': self.payment_ids[0].partner_id.id,
            'credit': self.amount,
            'date_maturity': fields.Date.today(),
        }
        aml_obj.create(values)
        debit_account = self.env['account.journal'].search([
            ['name', '=', 'Cheque']
        ])
        values = {
            'account_id': debit_account.default_debit_account_id.id,
            'name': move.ref,
            'move_id': move.id,
            'partner_id': self.payment_ids[0].partner_id.id,
            'debit': self.amount,
            'date_maturity': fields.Date.today(),
        }
        aml_obj.create(values)
        # move.post()

    def reject(self):
            # objs = self.env['account.move'].search([('journal_parent', '=', self.id)])
            # for obj in objs:
            #     obj.reverse_moves()
            # self.state_in = 'reject'
            aml_obj = self.env['account.move.line'].with_context(
                check_move_validity=False)
            account_values = {
                'date': self.date,
                'ref': 'reversal of journal entry.',#self.cheque_number,
                'journal_id': self.journal_id.id,
                'journal_parent': self.id
            }
            move = self.env['account.move'].create(account_values)

            IrDefault = self.env['ir.default'].sudo()

            transfer_account = IrDefault.get(
                'account.batch.deposit', 'account_id_transfer_intermediate', company_id=self.env.user.company_id.id)
            values = {
                'account_id': transfer_account,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            values = {
                'account_id': self.payment_ids[0].partner_id.property_account_receivable_id.id,#journal_id.default_debit_account_id.id,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            # move.post()
            self.state_in = 'reject'

    @api.one
    def pay_close(self):

        # aml_obj = self.env['account.move.line'].with_context(
        #     check_move_validity=False)
        # values = self.get_move_vals()
        # values.update({'ref': self.name,
        #                'journal_parent': self.id
        #                })
        # move = self.env['account.move'].create(values)
        # IrDefault = self.env['ir.default'].sudo()
        #
        # pay_debit_setting = IrDefault.get(
        #     'account.batch.deposit', 'pay_debit_setting', company_id=self.env.user.company_id.id)
        # pay_credit_setting = IrDefault.get(
        #     'account.batch.deposit', 'pay_credit_setting', company_id=self.env.user.company_id.id)
        #
        # values = {
        #     'account_id': pay_credit_setting,
        #     'name': move.ref,
        #     'move_id': move.id,
        #     'partner_id': self.payment_ids[0].partner_id.id,
        #     'help': 'a',
        #     'credit': self.amount,
        #     'date_maturity': fields.Date.today(),
        # }
        # aml_obj.create(values)
        # values = {
        #     'account_id': pay_debit_setting,
        #     'name': move.ref,
        #     'move_id': move.id,
        #     'partner_id': self.payment_ids[0].partner_id.id,
        #     'help': 'a',
        #     'debit': self.amount,
        #     'date_maturity': fields.Date.today(),
        # }
        # aml_obj.create(values)
        # move.post()
        # self.move_name = move.name
        # self.state_out = 'to_pay'
        # self.payment_ids.filtered(lambda r: r.state == 'draft').post()

        IrDefault = self.env['ir.default'].sudo()
        intermediate_account = IrDefault.get(
            'account.batch.deposit', 'account_id_receipt_intermediate_out', company_id=self.env.user.company_id.id)
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        values = self.get_move_vals()
        values.update({'ref': self.name,
                       })
        move = self.env['account.move'].create(values)

        acc = self.env['account.account'].search([('id', '=', intermediate_account)])
        print(acc, acc.name)
        print(intermediate_account, self.account_id_receipt_intermediate_out)#self.account_id_receipt_intermediate_out)#.id)#account_id_receipt_intermediate_out.id)
        print(self.payment_ids[0].partner_id.property_account_payable_id.id)
        for payment in self.payment_ids:
            values = {
                'account_id': intermediate_account,#self.account_id_receipt_intermediate_out.id, #self.pay_credit.id,
                'name': move.ref,
                'payment_id': payment.id,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            print('1 done')
            values = {
                'account_id': self.payment_ids[0].partner_id.property_account_payable_id.id,#account_id.id, #self.pay_debit.id,
                'name': move.ref,
                'payment_id': payment.id,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            print('2 done')
            # move.post()
            payment.state = 'posted'

        self.state_out = 'to_pay'
        # self.payment_ids.filtered(lambda r: r.state == 'draft').post()


    @api.one
    def make_close(self):
        print("account_id_transfer_intermediate",self.account_id_transfer_intermediate)
        print("account_id_receipt_intermediate",self.account_id_receipt_intermediate)
        print("account_id_receipt_intermediate_out",self.account_id_receipt_intermediate_out)
        print("account_id_transfer_intermediate_out",self.account_id_transfer_intermediate_out)

        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        values = self.get_move_vals()
        print("values",values)
        values.update({'ref': self.name,
                       'journal_parent': self.id
                       })
        move = self.env['account.move'].create(values)
        ###########***********######################

        IrDefault = self.env['ir.default'].sudo()

        pay_debit_setting = IrDefault.get(
            'account.batch.deposit', 'pay_debit_setting', company_id=self.env.user.company_id.id)
        pay_credit_setting = IrDefault.get(
            'account.batch.deposit', 'pay_credit_setting', company_id=self.env.user.company_id.id)

        ##############*********#####################


        if (self.journal_id and self.account_id_receipt_intermediate_out):
            values = {
                'account_id': self.journal_id.default_credit_account_id.id,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'credit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
            values = {
                'account_id': self.account_id_receipt_intermediate_out.id,
                'name': move.ref,
                'move_id': move.id,
                'partner_id': self.payment_ids[0].partner_id.id,
                'help': 'a',
                'debit': self.amount,
                'date_maturity': fields.Date.today(),
            }
            aml_obj.create(values)
        # move.post()
        self.move_name = move.name
        self.state_out = 'close'

    @api.one
    def normalize_payments(self):
        # Make sure all payments have batch_deposit as payment method (a payment created via the form view of the
        # payment_ids many2many of the batch deposit form view cannot receive a default_payment_method in context)
        self.payment_ids.write(
            {'payment_method_id': self.env.ref('payement_cheque.account_payment_method_cheque_in').id})
        if self.cheque_type=='out':
            self.payment_ids.write({'payment_type': 'outbound'})

        if self.cheque_type=='in':
            self.payment_ids.write({'payment_type': 'inbound'})

        # Since a batch deposit has no confirmation step (it can be used to select payments in a bank reconciliation
        # as long as state != reconciled), its payments need to be posted
        #self.payment_ids.filtered(lambda r: r.state == 'draft').post()


class config_cheque(models.TransientModel):
    _inherit = 'res.config.settings'

    rec_account_1 = fields.Many2one(
        'account.account', string="Recieve Debit Account")
    rec_account_2 = fields.Many2one(
        'account.account', string="Recieve Credit Account")



    intermediate_account = fields.Many2one(
        'account.account', string=" Receipt Intermediate Account",
        company_dependent=True)

    transfer_account = fields.Many2one(
        'account.account', string=" Transfer Intermediate Account",
        company_dependent=True)

    intermediate_account_out = fields.Many2one(
        'account.account', string=" Receipt Intermediate Account 2",
        company_dependent=True)

    transfer_account_out = fields.Many2one(
        'account.account', string=" Transfer Intermediate Account 2",
        company_dependent=True)

    cheque_draft_journal_id = fields.Many2one('account.journal', "Journal in Draft State", company_dependent=True)

    pay_debit_setting = fields.Many2one(
        'account.account', string="Pay Debit Account")
    pay_credit_setting = fields.Many2one(
        'account.account', string="Pay Credit Account")



    @api.model
    def get_values(self):
        res = super(config_cheque, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        #ICPSudo = self.env['ir.config_parameter'].sudo()
        cheque_draft_journal_id= IrDefault.get(
            'account.batch.deposit', 'cheque_draft_journal_id', company_id = self.company_id.id or self.env.user.company_id.id)
        intermediate_account = IrDefault.get(
            'account.batch.deposit','account_id_receipt_intermediate', company_id=self.company_id.id or self.env.user.company_id.id)

        transfer_account = IrDefault.get(
            'account.batch.deposit','account_id_transfer_intermediate', company_id=self.company_id.id or self.env.user.company_id.id)
        intermediate_account_out = IrDefault.get(
            'account.batch.deposit', 'account_id_receipt_intermediate_out',
            company_id=self.company_id.id or self.env.user.company_id.id)

        transfer_account_out = IrDefault.get(
            'account.batch.deposit', 'account_id_transfer_intermediate_out',
            company_id=self.company_id.id or self.env.user.company_id.id)

        rec_account_1 = IrDefault.get(
            'account.batch.deposit', 'rec_account_1',
            company_id=self.company_id.id or self.env.user.company_id.id)

        rec_account_2 = IrDefault.get(
            'account.batch.deposit', 'rec_account_2',
            company_id=self.company_id.id or self.env.user.company_id.id)
        pay_debit_setting = IrDefault.get(
            'account.batch.deposit', 'pay_debit_setting',
            company_id=self.company_id.id or self.env.user.company_id.id)

        pay_credit_setting = IrDefault.get(
            'account.batch.deposit', 'pay_credit_setting',
            company_id=self.company_id.id or self.env.user.company_id.id)









        res.update(
            cheque_draft_journal_id=cheque_draft_journal_id if cheque_draft_journal_id else False,
            intermediate_account=intermediate_account if intermediate_account else False,
            transfer_account=transfer_account if transfer_account else False,
            intermediate_account_out=intermediate_account_out if intermediate_account_out else False,
            transfer_account_out=transfer_account_out if transfer_account_out else False,
            rec_account_1=rec_account_1 if rec_account_1 else False,
            rec_account_2=rec_account_2 if rec_account_2 else False,
            pay_debit_setting = pay_debit_setting if pay_debit_setting else False,
            pay_credit_setting = pay_credit_setting if pay_credit_setting else False


        )
        return res

    @api.multi
    def set_values(self):
        super(config_cheque, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set(
            'account.batch.deposit', 'cheque_draft_journal_id', self.cheque_draft_journal_id.id, company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit','account_id_receipt_intermediate', self.intermediate_account.id,company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit','account_id_transfer_intermediate', self.transfer_account.id,company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit', 'account_id_receipt_intermediate_out', self.intermediate_account_out.id,
            company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit', 'account_id_transfer_intermediate_out', self.transfer_account_out.id,
            company_id=self.company_id.id)

        IrDefault.set(
            'account.batch.deposit', 'rec_account_1', self.rec_account_1.id,
            company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit', 'rec_account_2', self.rec_account_2.id,
            company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit', 'pay_debit_setting', self.pay_debit_setting.id,
            company_id=self.company_id.id)
        IrDefault.set(
            'account.batch.deposit', 'pay_credit_setting', self.pay_credit_setting.id,
            company_id=self.company_id.id)


class ChequeStatusHistory(models.TransientModel):
    _name = 'account.batch.deposit.history'
    _description = 'Cheque Status History'

    compute_at_date = fields.Selection([
        (0, 'Current Date'),
        (1, 'At a Specific Date')
    ],
        string="Compute",
        help="Choose to analyze the current cheques \
    or from a specific date in the past."
    )
    date = fields.Datetime(
        'Cheques at Date',
        help="Choose a date to get the cheques at that date",
        default=fields.Datetime.now()
    )



class match_state_reconcile_button(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def process_reconciliations(self, data):
        """ Used to validate a batch of reconciliations in a single call
            :param data: list of dicts containing:
                - 'type': either 'partner' or 'account'
                - 'id': id of the affected res.partner or account.account
                - 'mv_line_ids': ids of exisiting account.move.line to reconcile
                - 'new_mv_line_dicts': list of dicts containing values suitable for account_move_line.create()
        """
        print("datadadatadatadata", data)
        print("rrrrrrrrrrrrrrrrrrrrrrttttttttttt",data[0]['mv_line_ids'])
        for line in data[0]['mv_line_ids']:
            print("zzzaaa")
            print(line)
            move = self.env['account.move.line'].browse(line)
            print(move)
            print(move[0].payment_id)
            print(move[0].name)
            if move.payment_id:
                move.payment_id.state='matched'
            # payment = self.env['account.payment'].search([('id','=',move.payment_id.id)])
            # print('pppppppppppppppppppppaymmmmment',payment)
            # if payment:
            #     payment.state='matched'
        for datum in data:
            if len(datum['mv_line_ids']) >= 1 or len(datum['mv_line_ids']) + len(datum['new_mv_line_dicts']) >= 2:
                self.browse(datum['mv_line_ids']).process_reconciliation(datum['new_mv_line_dicts'])

            if datum['type'] == 'partner':
                partners = self.env['res.partner'].browse(datum['id'])
                partners.mark_as_reconciled()
            if datum['type'] == 'account':
                accounts = self.env['account.account'].browse(datum['id'])
                accounts.mark_as_reconciled()

    # def open_table(self):
    #     self.ensure_one()
    #
    #     # if not self.compute_at_date:
    #     #     self.date =
    #     tree_view_id = self.env.ref('payement_cheque.batch_view_tree').id
    #     form_view_id = self.env.ref('payement_cheque.cheque_batch_view').id
    #     # We pass `to_date` in the context
    #     # so that `qty_available` will be computed across
    #     # moves until date.
    #     action = {
    #         'type': 'ir.actions.act_window',
    #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #         'view_mode': 'tree,form',
    #         'name': _('Cheques'),
    #         'res_model': 'account.batch.deposit',
    #         'context': dict(self.env.context, to_date=self.date),
    #         'domain': [('create_date', '<=', self.date)]
    #     }
    #     return action
        # else:
        #     self.env['stock.quant']._merge_quants()
        #     return self.env.ref('stock.quantsact').read()[0]


# class RegisterPayment(models.TransientModel):
#     _name = "account.register.payments"
#     # _inherit = "account.payment"
