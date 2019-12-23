# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import UserError

class transaction_dates_purchase(models.Model):
    _inherit = 'purchase.order'

    def _compute_flag_ro_defalut(self):
        if self.env.user.has_group('transaction_dates.edit_trans_date_groups'):
            return True
        else:
            return False

    @api.multi
    def _compute_flag_ro(self):
        for rec in self:
            print(rec.env.user.has_group('transaction_dates.edit_trans_date_groups'), 'USER GROUP')
            if rec.env.user.has_group('transaction_dates.edit_trans_date_groups'):
                rec.flag = True
            else:
                rec.flag = False


    flag = fields.Boolean(default=_compute_flag_ro_defalut, compute='_compute_flag_ro')

# bills

class transaction_dates_bills(models.Model):
    _inherit = 'account.invoice'

    def _compute_flag_ro_defalut(self):
        if self.env.user.has_group('transaction_dates.edit_trans_date_groups'):
            return True
        else:
            return False

    @api.multi
    def _compute_flag_ro(self):
        for rec in self:
            print(rec.env.user.has_group('transaction_dates.edit_trans_date_groups'), 'USER GROUP')
            if rec.env.user.has_group('transaction_dates.edit_trans_date_groups'):
                rec.flag = True
            else:
                rec.flag = False

    flag = fields.Boolean(default=_compute_flag_ro_defalut, compute='_compute_flag_ro')

    # date_invoice = fields.Date(string='Invoice Date',
    #                            readonly=True, states={'draft': [('readonly', False)]}, index=True,
    #                            help="Keep empty to use the current date", copy=False)
    # date_invoice = fields.Date(string='Invoice Date',
    #                            help="Keep empty to use the current date")

#journal entry
class transaction_dates_journal(models.Model):
    _inherit = 'account.move'

    def _compute_flag_ro_defalut(self):
        if self.env.user.has_group('transaction_dates.edit_trans_date_groups'):
            return True
        else:
            return False

    @api.multi
    def _compute_flag_ro(self):
        for rec in self:
            print(rec.env.user.has_group('transaction_dates.edit_trans_date_groups'), 'USER GROUP')
            if rec.env.user.has_group('transaction_dates.edit_trans_date_groups'):
                rec.flag = True
            else:
                rec.flag = False

    flag = fields.Boolean(default=_compute_flag_ro_defalut, compute='_compute_flag_ro')

#analytic entry
class transaction_dates_analytic(models.Model):
    _inherit = 'account.analytic.line'

    def _compute_flag_ro_defalut(self):
        if self.env.user.has_group('transaction_dates.edit_trans_date_groups'):
            return True
        else:
            return False

    @api.multi
    def _compute_flag_ro(self):
        for rec in self:
            print(rec.env.user.has_group('transaction_dates.edit_trans_date_groups'), 'USER GROUP')
            if rec.env.user.has_group('transaction_dates.edit_trans_date_groups'):
                rec.flag = True
            else:
                rec.flag = False

    flag = fields.Boolean(default=_compute_flag_ro_defalut, compute='_compute_flag_ro')

#payment
class transaction_dates_payment(models.Model):
    _inherit = 'account.payment'

    def _compute_flag_ro_defalut(self):
        if self.env.user.has_group('transaction_dates.edit_trans_date_groups'):
            return True
        else:
            return False

    @api.multi
    def _compute_flag_ro(self):
        for rec in self:
            print(rec.env.user.has_group('transaction_dates.edit_trans_date_groups'), 'USER GROUP')
            if rec.env.user.has_group('transaction_dates.edit_trans_date_groups'):
                rec.flag = True
            else:
                rec.flag = False

    flag = fields.Boolean(default=_compute_flag_ro_defalut, compute='_compute_flag_ro')




