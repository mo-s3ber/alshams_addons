# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_journal(self):
        journal_type = self._context.get('journal_type', False)
        progress_invoice = self._context.get('default_progress_invoice', False)
        company_id = self._context.get('company_id', self.env.user.company_id.id)

        if journal_type and journal_type == 'purchase' and progress_invoice:
            return self.env['account.journal'].search(
                [('type', '=', 'purchase'), ('progress_invoice', '=', True), ('company_id', '=', company_id)],
                limit=1)
        else:
            return super(AccountInvoice, self)._default_journal()

    # @api.one
    # @api.depends('partner_id', 'subcontract_requisition_id')
    # def _compute_former_invoice(self):
    #     domain = [('partner_id', '=', self.partner_id.id), ('progress_invoice', '=', True), ('state', 'not in', ['draft', 'cancel'])]
    #     if self.subcontract_requisition_id:
    #         domain.append(('subcontract_requisition_id', '=', self.subcontract_requisition_id.id))
    #     self.former_invoice_id = self.search(domain, limit=1, order="id desc")

    @api.one
    @api.depends('partner_id')
    def _compute_balance(self):
        moawlyen_account_code = 21004
        domain = [('code', '=', moawlyen_account_code),
                  ('internal_type', 'in', ['receivable', 'payable'])]
        account_ids = self.env['account.account'].search(domain)
        domain = [('analytic_account_id', '=', self.account_analytic_id.id),
                  ('partner_id', '=', self.partner_id.id),
                  ('company_id', '=', self.company_id.id)]
        move_line_ids = self.env['account.move.line'].search(domain).filtered(
            lambda r: r.account_id.id in account_ids.ids)
        self.partner_balance = sum(move_line_ids.mapped('debit')) - sum(move_line_ids.mapped('credit'))

    @api.one
    # @api.depends('partner_balance', 'amount_total')
    def _compute_est_balance(self):
        self.est_balance = (self.partner_balance or 0.0) - self.amount_total

    # state = fields.Selection(selection_add=[('waiting_inv_approval', 'Waiting Approval'), ('inv_approved', 'Approved')])
    state = fields.Selection([
            ('draft','Draft'),
            ('waiting_inv_approval', 'Waiting Approval'),
            ('inv_approved', 'Approved'),
            ('open', 'Open'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Project')
    progress_type = fields.Selection([('ongoing', 'Ongoing'), ('final', 'Final'), ('opening', 'Opening')],
                                     string='Progress Type')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    partner_account = fields.Many2one(related="partner_id.property_account_payable_id")
    payment_ref = fields.Char('Payment Reference')
    partner_balance = fields.Monetary(string='Partner Balance', compute=_compute_balance)
    former_invoice_id = fields.Many2one('account.invoice', string='Former Invoice')
    # former_invoice_id = fields.Many2one('account.invoice', string='Former Invoice', compute=_compute_former_invoice, store=True)
    progress_invoice = fields.Boolean('Progress Invoice')
    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_journal,
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
    sequence_number_next = fields.Char(string='Next Number', compute="_get_sequence_number_next", inverse="_set_sequence_next", readonly=True, store=True)
    number = fields.Char('Number')
    number2 = fields.Char('Number')
    est_balance = fields.Monetary(string='Estimated Balance', compute=_compute_est_balance)

    def send_inv_approval(self):
        self.state = "waiting_inv_approval"

    def confirm_inv_approval(self):
        if self.user_has_groups('progress_invoice.group_manage_inv_approval'):
            self.state = "inv_approved"
        else:
            raise Warning("You don't have permission to approve. please enable from User Settings")

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()

        for inv in self:
            if inv.subcontract_requisition_id and inv.progress_invoice:
                for line in inv.invoice_line_ids:
                    requisition_line_ids = inv.subcontract_requisition_id.line_ids.filtered(lambda r: r.product_id == line.product_id and r.sequence == line.sequence )
                    requisition_line_ids._compute_ordered_qty()
                    requisition_line_ids._compute_ordered_price()
                    for scr_line in requisition_line_ids:
                        if scr_line.product_qty < scr_line.qty_invoiced:
                            raise Warning(_("You can't exceed the Contract quantity, please contact your administrator."))
                        if (scr_line.product_qty * scr_line.price_unit) < scr_line.price_invoiced:
                            raise Warning(_("You can't exceed the Contract amount, please contact your administrator"))
        return res

    @api.onchange('partner_id', 'subcontract_requisition_id')
    def _onchange_subcontract_requisition_id(self):
        former_invoice_id = False
        domain = [('progress_invoice', '=', True), ('state', 'not in', ['draft', 'cancel'])]
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.subcontract_requisition_id:
            domain.append(('subcontract_requisition_id', '=', self.subcontract_requisition_id.id))
        if self.partner_id or self.subcontract_requisition_id:
            former_invoice_id = self.search(domain, limit=1, order="id desc")
        return {
            'value': {'former_invoice_id': former_invoice_id},
            'domain': {'former_invoice_id': [('subcontract_requisition_id', '=', self.subcontract_requisition_id and self.subcontract_requisition_id.id)]},
        }

    @api.multi
    def xmlrpc_onchange_invoice_line_ids(self):
        self._onchange_invoice_line_ids()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('invoice_id.former_invoice_id')
    def _get_previous_qty(self):
        if self.invoice_id.former_invoice_id:
            lines = self.invoice_id.former_invoice_id.invoice_line_ids.filtered(lambda r: r.product_id.id == self.product_id.id and r.line_sequence == self.line_sequence and r.price_unit == self.price_unit)
            self.prev_qty = sum(lines.mapped('total_qty'))
        else:  # if not self.invoice_id.former_invoice_id:

            contract_ids = self.env['subcontract.requisition'].search([('id', '=', self.invoice_id.subcontract_requisition_id.id)])
            for rec in self:
                for contract in contract_ids.line_ids:
                    if rec.product_id.id == contract.product_id.id and rec.line_sequence==contract.sequence:
                        rec.prev_qty = contract.previ_qty#rec.invoice_id.subcontract_requisition_id.previ_qty

    @api.multi
    def xmlrpc_compute_total_qty(self):
        self._get_total_qty()
        return True

    @api.one
    @api.depends('prev_qty', 'quantity')
    def _get_total_qty(self):
        self.total_qty = self.quantity + self.prev_qty

    @api.one
    @api.depends('invoice_id.former_invoice_id')
    def _get_previous_amount(self):
        if self.invoice_id.former_invoice_id:
            lines = self.invoice_id.former_invoice_id.invoice_line_ids.filtered(lambda r: r.product_id.id == self.product_id.id and r.line_sequence == self.line_sequence and r.price_unit == self.price_unit)
            self.prev_amount = sum(lines.mapped('total_amount'))
        else:  # if self.invoice_id.former_invoice_id == False:

            contract_ids = self.env['subcontract.requisition'].search(
                [('id', '=', self.invoice_id.subcontract_requisition_id.id)])
            for rec in self:
                for contract in contract_ids.line_ids:
                    if rec.product_id.id == contract.product_id.id and rec.line_sequence==contract.sequence:
                        rec.prev_amount = contract.previ_amount
            # self.prev_amount = self.invoice_id.subcontract_requisition_id.prev_amount



    @api.one
    @api.depends('price_unit', 'total_qty', 'percentage')
    def _get_total_amount(self):
        percentage = (self.percentage / 100) if self.percentage else 1
        self.total_amount = self.price_unit * self.total_qty * percentage

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date',
                 'prev_amount', 'total_amount')
    def _compute_price(self):
        super(AccountInvoiceLine, self)._compute_price()
        if self.invoice_id.progress_invoice:
            self.price_subtotal = self.total_amount - self.prev_amount

    cost_code = fields.Many2one('subcontract.code', string="Cost Code")
    prev_qty = fields.Float('Previous Quantity', compute='_get_previous_qty')
    percentage = fields.Float('Percentage')
    total_qty = fields.Float('Total Quantity', store=True, compute='_get_total_qty')
    prev_amount = fields.Monetary(string='Previous Amount', compute='_get_previous_amount')
    total_amount = fields.Monetary(string='Total Amount', store=True, compute='_get_total_amount')

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    progress_invoice = fields.Boolean('Is Progress Invoice?')
