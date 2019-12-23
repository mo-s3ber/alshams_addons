from odoo import models, api, fields, _
from datetime import datetime
from odoo.exceptions import UserError, RedirectWarning, Warning


class AccountMove(models.Model):
    _inherit = "account.move"

    guarantee_id = fields.Many2one('letter.guarantee')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    guarantee_account_id = fields.Many2one('account.account', string="Account")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        guarantee = params.get_param('guarantee_account_id')

        res.update(
            guarantee_account_id=guarantee and int(guarantee) or '',
        )
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('guarantee_account_id',
                                                         self.guarantee_account_id and self.guarantee_account_id.id or '')


class LetterOfGuarantee(models.Model):
    _name = 'letter.guarantee'

    @api.depends('percent_insurance', 'amount_total_start', 'deduction_ids')
    def _compute_total_current(self):
        deductions = sum(self.deduction_ids.filtered(lambda r: r.state == 'posted').mapped('amount_total'))
        try:
            if deductions and self.percent_insurance:
                self.amount_total_current = self.amount_total_start - (deductions / (self.percent_insurance / 100.0))
            else:
                self.amount_total_current = self.amount_total_start
            self.amount_insurance_start = self.amount_total_start * (self.percent_insurance / 100.0)
            self.amount_insurance_current = self.amount_total_current * (self.percent_insurance / 100.0)
            self.amount_total_deduction = deductions
        except Exception as e:
            pass

    def _default_analytic_id(self):
        try:
            return int(self.env['ir.config_parameter'].sudo().get_param('analytical_id'))
        except Exception as e:
            pass

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Running'),
        ('closed', 'Closed'), ], string='Status', index=True, readonly=True, default='draft')
    name = fields.Char(string="LG Name / No")
    code = fields.Char(string="Short Name")
    partner_id = fields.Many2one('res.partner', string="Issue to", required=True)
    ref = fields.Char(string="Reference", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    analytic_account_id = fields.Many2one('account.analytic.account', default=_default_analytic_id, string="Project",
                                          required=True)
    analytic_group_id = fields.Many2one('account.analytic.group', string="Analytical group")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    type = fields.Selection(([('advanced_prepayment', 'Advanced Prepayment'), ('bid_bond', 'Bid bond'),
                              ('performance', 'Performance'), ('retention', 'Retention')]), string="Letter Type",
                            required=True)
    journal_id = fields.Many2one('account.journal', string="Bank", required=True, domain="[('type','=','bank')]")
    date_issue = fields.Date(string="Issue Date")
    date_expire = fields.Date(string="Expiration Date")
    amount_total_start = fields.Monetary(string="Start Total Amount", required=True, store=True,
                                         currency_field='currency_id')
    amount_total_current = fields.Monetary(compute=_compute_total_current, string="Current Total Amount", store=True,
                                           currency_field='currency_id')
    percent_insurance = fields.Float(string="Insurance Percent %")
    amount_insurance_start = fields.Monetary(compute=_compute_total_current, string="Start Insurance amount",
                                             store=True,
                                             currency_field='currency_id')
    amount_insurance_current = fields.Monetary(compute=_compute_total_current, string="Current Insurance Amount",
                                               store=True, currency_field='currency_id')
    amount_total_deduction = fields.Monetary(compute=_compute_total_current, string="Deduction Amount",
                                             store=True, currency_field='currency_id')
    deduction_ids = fields.One2many('letter.guarantee.deduction', 'guarantee_id', string="LG Deduction",
                                    ondelete="cascade")
    journal_count = fields.Integer(compute='_compute_journal_count', string='#  Journal Entries')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('letter.guarantee') or '/'
        vals['ref'] = seq
        return super(LetterOfGuarantee, self).create(vals)

    def issue_lg(self):
        guarantee_account_id = self.env['ir.config_parameter'].sudo().get_param('guarantee_account_id')
        if not guarantee_account_id:
            raise Warning('Please Select Letter of Guarantee Account under configuration')
        if not self.journal_id.default_credit_account_id:
            raise Warning("Credit account not set in Bank")

        move = self.env['account.move'].create({
            'date': datetime.now(),
            'ref': self.ref,
            'journal_id': self.journal_id.id,
            'guarantee_id': self.id,
            'line_ids': [(0, 0, {'account_id': int(guarantee_account_id),
                                 'partner_id': self.partner_id.id,
                                 'analytic_account_id': self.analytic_account_id.id,
                                 'debit': self.amount_insurance_current}),
                         (0, 0, {'account_id': self.journal_id.default_credit_account_id.id,
                                 'partner_id': self.partner_id.id,
                                 'analytic_account_id': self.analytic_account_id.id,
                                 'credit': self.amount_insurance_current})]
        })
        move.action_post()
        self.state = "open"

    def close_payment(self):
        self.state = "closed"

    def close_lg(self):
        guarantee_account_id = int(self.env['ir.config_parameter'].sudo().get_param('guarantee_account_id'))

        if not guarantee_account_id:
            raise Warning('Please Select Letter of Guarantee Account under configuration')

        if not self.journal_id.default_credit_account_id:
            raise Warning("Credit account not set in Bank")

        move = self.env['account.move'].create({
            'date': datetime.now(),
            'ref': self.ref,
            'journal_id': self.journal_id.id,
            'state': 'posted',
            'guarantee_id': self.id,
            'line_ids': [
                (0, 0, {'account_id': int(guarantee_account_id),
                        'partner_id': self.partner_id.id,
                        'analytic_account_id': self.analytic_account_id.id,
                        'credit': self.amount_insurance_current}),
                (
                    0, 0, {'account_id': self.journal_id.default_credit_account_id.id, 'partner_id': self.partner_id.id,
                           'analytic_account_id': self.analytic_account_id.id,
                           'debit': self.amount_insurance_current})]
        })
        move.action_post()
        self.state = "closed"

    def _compute_journal_count(self):
        for each in self:
            each.journal_count = len(self.env['account.move'].search([('guarantee_id', '=', each.id)]))

    @api.multi
    def open_moves(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Journal Entries'),
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('guarantee_id', 'in', self.ids)],
                'views': [[False, 'tree'], [False, 'form']],
                }


class LetterOfDeduction(models.Model):
    _name = "letter.guarantee.deduction"

    ref = fields.Char(string="Reference")
    date = fields.Date(string="Payment Date")
    journal_id = fields.Many2one('account.journal', related='guarantee_id.journal_id', readonly=True, string="Payment Journal")
    memo = fields.Char(string="Memo")
    amount_total = fields.Integer(string="Payment Amount")
    guarantee_id = fields.Many2one('letter.guarantee', string='Journal Entry', ondelete="cascade")
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string='Status', default='draft')

    @api.multi
    def confirm(self):
        guarantee_account_id = int(self.env['ir.config_parameter'].sudo().get_param('guarantee_account_id'))

        if not guarantee_account_id:
            raise Warning('Please Select Letter of Guarantee Account under configuration')

        if not self.journal_id.default_credit_account_id:
            raise Warning("Credit account not set in Bank")

        move = self.env['account.move'].create({
            'date': datetime.now(),
            'ref': self.ref,
            'journal_id': self.journal_id.id,
            'guarantee_id': self.guarantee_id.id,
            'line_ids': [
                (0, 0, {'account_id': int(guarantee_account_id),
                        'partner_id': self.guarantee_id.partner_id.id,
                        'analytic_account_id': self.guarantee_id.analytic_account_id.id,
                        'credit': self.amount_total}),
                (
                    0, 0, {'account_id': self.journal_id.default_credit_account_id.id,
                           'partner_id': self.guarantee_id.partner_id.id,
                           'analytic_account_id': self.guarantee_id.analytic_account_id.id,
                           'debit': self.amount_total})]
        })
        move.action_post()
        self.state = 'posted'

    @api.multi
    def write(self, vals):
        res = super(LetterOfDeduction, self).write(vals)
        if self.state == 'posted':
            self.guarantee_id._compute_total_current()
        return res

    @api.multi
    def unlink(self):
        for each in self:
            if each.state == 'posted':
                raise Warning(_('You cannot delete in status "Posted"'))
        return super(LetterOfDeduction, self).unlink()


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_analytic_id = fields.Many2one('account.analytic.account', string="LG Account")
