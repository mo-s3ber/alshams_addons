# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime


class stock_backorder_confirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    transfer_date = fields.Datetime(string='Transfer Date', default=fields.Datetime.now)
    remark = fields.Char('Remark')

    @api.multi
    def _process(self, cancel_backorder=False):
        self.pick_ids.tra_date = self.transfer_date
        res = super(stock_backorder_confirmation, self)._process(
            cancel_backorder=cancel_backorder)
        if self.pick_ids:
            if not self.transfer_date:
                self.transfer_date = datetime.now()

            for line in self.pick_ids.move_lines:
                line.write({'remark': self.remark,
                            'date_expected': self.transfer_date,'date':self.transfer_date})

            for pack in self.pick_ids.move_line_ids:
                pack.write({'remark': self.remark,
                            'date_expected': self.transfer_date,'date':self.transfer_date})
        return res


class stock_immediate_transfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    transfer_date = fields.Datetime(string='Transfer Date', default=fields.Datetime.now)
    remark = fields.Char('Remark')
    direct = fields.Boolean('Direct')

    @api.multi
    def process(self):
        self.pick_ids.tra_date = self.transfer_date
        if self.direct:
            for pick in self.pick_ids:
                pick.action_done()
        else:
            res = super(stock_immediate_transfer, self).process()
        if self.pick_ids:
            if not self.transfer_date:
                self.transfer_date = datetime.now()

            for line in self.pick_ids.move_lines:
                line.write({'remark': self.remark,
                            'date_expected': self.transfer_date,'date':self.transfer_date})

            for pack in self.pick_ids.move_line_ids:
                pack.write({'remark': self.remark,
                            'date_expected': self.transfer_date,'date':self.transfer_date})

        if not self.direct:
            return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
