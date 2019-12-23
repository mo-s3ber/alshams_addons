from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError




class account_move_line_inherit(models.Model):
    _inherit = 'account.move.line'
    @api.multi
    def write(self, vals):
        if ('account_id' in vals) and self.env['account.account'].browse(vals['account_id']).deprecated:
            raise UserError(_('You cannot use deprecated account.'))
        if any(key in vals for key in ('account_id', 'journal_id', 'date', 'move_id', 'debit', 'credit')):
            self._update_check()
        if not self._context.get('allow_amount_currency') and any \
                        (key in vals for key in ('amount_currency', 'currency_id')):
            # hackish workaround to write the amount_currency when assigning a payment to an invoice through the 'add' button
            # this is needed to compute the correct amount_residual_currency and potentially create an exchange difference entry
            self._update_check()
        # when we set the expected payment date, log a note on the invoice_id related (if any)
        if vals.get('expected_pay_date') and self.invoice_id:
            msg = _('New expected payment date: ') + vals['expected_pay_date'] + '.\n' + vals.get('internal_note', '')
            self.invoice_id.message_post(body=msg)  # TODO: check it is an internal note (not a regular email)!
        # when making a reconciliation on an existing liquidity journal item, mark the payment as reconciled
        for record in self:
            if 'statement_line_id' in vals and record.payment_id:
                # In case of an internal transfer, there are 2 liquidity move lines to match with a bank statement
                # if all(line.statement_id for line in record.payment_id.move_line_ids.filtered
                #         (lambda r: r.id != record.id and r.account_id. internal_type =='liquidity')):
                    record.payment_id.state = 'reconciled'

        result = super(account_move_line_inherit, self).write(vals)
        if self._context.get('check_move_validity', True) and any \
                        (key in vals for key in ('account_id', 'journal_id', 'date', 'move_id', 'debit', 'credit')):
            move_ids = set()
            for line in self:
                if line.move_id.id not in move_ids:
                    move_ids.add(line.move_id.id)
            self.env['account.move'].browse(list(move_ids))._post_validate()
        return result