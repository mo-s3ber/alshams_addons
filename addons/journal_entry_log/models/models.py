# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TrackJournalEntry(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread', 'mail.activity.mixin', 'portal.mixin']

    ref = fields.Char(string='Reference', copy=False, track_visibility='onchange')
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True,
                       default=fields.Date.context_today, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 states={'posted': [('readonly', True)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', store=True,
                                 readonly=True, track_visibility='onchange')
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',
                               states={'posted': [('readonly', True)]}, track_visibility='onchange', copy=True)
    state = fields.Selection(track_visibility='onchange')


class TrackJournalEntryLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, values):
        line = super(TrackJournalEntryLine, self).create(values)
        msg = _("Extra line with %s ") % (line.analytic_account_id.display_name,)
        line.move_id.message_post(body=msg)

        return line

    @api.multi
    def write(self, values):
        # if 'analytic_account_id' in values:
        for line in self:
            if 'analytic_account_id' in values:
                new_analytic_account = self.env['account.analytic.account'].browse(values['analytic_account_id'])
            else:
                new_analytic_account = False

            if 'account_id' in values:
                new_account = self.env['account.account'].browse(values['account_id'])
            else:
                new_account = False

            if 'partner_id' in values:
                new_partner = self.env['res.partner'].browse(values['partner_id'])
            else:
                new_partner = False

            data = {'line': line, 'new_analytic_account': new_analytic_account, 'new_account': new_account,
                    'new_partner': new_partner, 'new_label': values.get('name', 0), 'new_debit': values.get('debit', 0),
                    'new_credit': values.get('credit', 0)}
            line.move_id.message_post_with_view('journal_entry_log.track_am_line_template',
                                                values=data,
                                                subtype_id=self.env.ref('mail.mt_note').id)

        return super(TrackJournalEntryLine, self).write(values)
