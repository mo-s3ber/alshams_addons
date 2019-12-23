# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FixCreditDebitValues(models.Model):
    _inherit = 'account.move'

    @api.multi
    def write(self, vals):
        if 'line_ids' in vals:
            flag_new_line_added = 0
            for line in vals['line_ids']:
                if line[0] == flag_new_line_added:
                    line[2]['credit'] = round(line[2]['credit'], 3)
                    line[2]['debit'] = round(line[2]['debit'], 3)

            res = super(FixCreditDebitValues, self.with_context(check_move_validity=False)).write(vals)
            self.assert_balanced()
        else:
            res = super(FixCreditDebitValues, self).write(vals)
        return res
