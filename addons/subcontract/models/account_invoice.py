# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.addons.account.models.account_invoice import AccountInvoice
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountInvoiceAllowNegativeTotal(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: not inv.progress_invoice and inv.state != 'draft'):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(lambda inv: inv.progress_invoice and inv.state != 'inv_approved'):
            raise UserError(_("Invoice must be in approved state in order to validate it."))
        #if to_open_invoices.filtered(
        #        lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
        #    raise UserError(_(
        #        "You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _('No account was found to create the invoice, be sure you have installed a chart of account.'))

        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    progress_invoice_id = fields.Many2one('account.invoice', string='Vendor Bill',
                                          help="Auto-complete from a past bill.")
    subcontract_id = fields.Many2one(
        comodel_name='subcontract.order',
        string='Add Subcontract Order',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Load the subcontractor bill based on selected subcontract order. Several CO can be selected.'
    )
    progress_invoice_subcontract_id = fields.Many2one(
        comodel_name='subcontract.bill.union',
        string='Auto-Complete'
    )

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        pass
        #for inv in self:
        #    if float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1:
        #        raise Warning(_(
        #            'You cannot validate an invoice with a negative total amount. You should create a credit note instead.'))

    @api.onchange('progress_invoice_subcontract_id')
    def _onchange_bill_subcontract_order(self):
        if not self.progress_invoice_subcontract_id:
            return {}
        self.subcontract_id = self.progress_invoice_subcontract_id.subcontract_order_id
        self.progress_invoice_id = self.progress_invoice_subcontract_id.progress_invoice_id
        self.progress_invoice_subcontract_id = False
        return {}

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_subcontract_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        subcontract orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        subcontract_line_ids = self.invoice_line_ids.mapped('subcontract_line_id')
        subcontract_ids = self.invoice_line_ids.mapped('subcontract_id').filtered(
            lambda r: r.order_line <= subcontract_line_ids)

        domain = [('invoice_status', 'in', ['to invoice', 'no'])]
        if self.partner_id:
            domain += [('partner_id', 'child_of', self.partner_id.id)]
        if subcontract_ids:
            domain += [('id', 'not in', subcontract_ids.ids)]
        result['domain'] = {'subcontract_id': domain}
        return result

    def _prepare_invoice_line_from_co_line(self, line):
        if line.product_id.subcontract_method == 'subcontract':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.qty_received - line.qty_invoiced
        #if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
        #    qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes, line.product_id,
                                                                        line.order_id.partner_id)
        invoice_line = self.env['account.invoice.line']
        date = self.date or self.date_invoice
        data = {
            'subcontract_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context(
                {'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id._convert(
                line.price_unit, self.currency_id, line.company_id, date or fields.Date.today(), round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids,
            'cost_code': line.cost_code_id and line.cost_code_id.id,
            'line_sequence':line.line_sequence
        }
        account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id,
                                                        self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    def _onchange_product_id(self):
        domain = super(AccountInvoice, self)._onchange_product_id()
        if self.subcontract_id:
            # Use the subcontract uom by default
            self.uom_id = self.product_id.uom_po_id
        return domain

    # Load all unsold CO lines
    @api.onchange('subcontract_id')
    def subcontract_order_change(self):
        if not self.subcontract_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.subcontract_id.partner_id.id

        if not self.invoice_line_ids:
            #as there's no invoice line yet, we keep the currency of the PO
            self.currency_id = self.subcontract_id.currency_id
        new_lines = self.env['account.invoice.line']
        for line in self.subcontract_id.order_line - self.invoice_line_ids.mapped('subcontract_line_id'):
            data = self._prepare_invoice_line_from_co_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.subcontract_id.payment_term_id
        self.env.context = dict(self.env.context, from_subcontract_order_change=True)
        # self.subcontract_id = False
        return {}

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.currency_id:
            for line in self.invoice_line_ids.filtered(lambda r: r.subcontract_line_id):
                date = self.date or self.date_invoice or fields.Date.today()
                company = self.company_id
                line.price_unit = line.subcontract_id.currency_id._convert(
                    line.subcontract_line_id.price_unit, self.currency_id, company, date, round=False)

    @api.onchange('invoice_line_ids')
    def _onchange_origin(self):
        subcontract_ids = self.invoice_line_ids.mapped('subcontract_id')
        if subcontract_ids:
            self.origin = ', '.join(subcontract_ids.mapped('name'))
            self.reference = ', '.join(subcontract_ids.filtered('partner_ref').mapped('partner_ref')) or self.reference


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        payment_term_id = self.env.context.get('from_subcontract_order_change') and self.payment_term_id or False
        res = super(AccountInvoice, self)._onchange_partner_id()
        if payment_term_id:
            self.payment_term_id = payment_term_id
        if not self.env.context.get('default_journal_id') and self.partner_id and self.currency_id and\
                self.type in ['in_invoice', 'in_refund'] and\
                self.currency_id != self.partner_id.property_subcontract_currency_id and\
                self.partner_id.property_subcontract_currency_id.id:
            journal_domain = [
                ('type', '=', 'subcontract'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.partner_id.property_subcontract_currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(journal_domain, limit=1)
            if default_journal_id:
                self.journal_id = default_journal_id
            if self.env.context.get('default_currency_id'):
                self.currency_id = self.env.context['default_currency_id']
        return res

    @api.model
    def create(self, vals):
        invoice = super(AccountInvoice, self).create(vals)
        subcontract = invoice.invoice_line_ids.mapped('subcontract_line_id.order_id')
        if subcontract and not invoice.refund_invoice_id:
            message = _("This progress invoice has been created from: %s") % (",".join(["<a href=# data-oe-model=subcontract.order data-oe-id=" + str(order.id) + ">" + order.name + "</a>" for order in subcontract]))
            invoice.message_post(body=message)
        return invoice


    @api.multi
    def write(self, vals):
        result = True
        for invoice in self:
            subcontract_old = invoice.invoice_line_ids.mapped('subcontract_line_id.order_id')
            result = result and super(AccountInvoice, invoice).write(vals)
            subcontract_new = invoice.invoice_line_ids.mapped('subcontract_line_id.order_id')
            #To get all po reference when updating invoice line or adding subcontract order reference from vendor bill.
            subcontract = (subcontract_old | subcontract_new) - (subcontract_old & subcontract_new)
            if subcontract:
                message = _("This progress invoice has been modified from: %s") % (",".join(["<a href=# data-oe-model=subcontract.order data-oe-id=" + str(order.id) + ">" + order.name + "</a>" for order in subcontract]))
                invoice.message_post(body=message)
        return result


class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the subcontract order line it is related to"""
    _inherit = 'account.invoice.line'

    subcontract_line_id = fields.Many2one('subcontract.order.line', 'Subcontract Order Line', ondelete='set null',
                                          index=True, readonly=True)
    subcontract_id = fields.Many2one('subcontract.order', related='subcontract_line_id.order_id',
                                     string='Subcontract Order', store=False, readonly=True, related_sudo=False,
                                     help='Associated Subcontract Order. Filled in automatically when a PO is chosen on the vendor bill.')
    line_sequence = fields.Integer(string="sequence")
