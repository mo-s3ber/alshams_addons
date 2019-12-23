from odoo import api, fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.multi
    def _compute_subcontract_order_count(self):
        SubcontractOrder = self.env['subcontract.order']
        for partner in self:
            partner.subcontract_order_count = SubcontractOrder.search_count([('partner_id', 'child_of', partner.id)])

    @api.multi
    def _compute_subcontract_supplier_invoice_count(self):
        Invoice = self.env['account.invoice']
        for partner in self:
            partner.subcontract_supplier_invoice_count = Invoice.search_count(
                [('partner_id', 'child_of', partner.id), ('type', '=', 'in_invoice')])

    @api.model
    def _commercial_fields(self):
        return super(res_partner, self)._commercial_fields()

    subcontractor = fields.Boolean(string='Is a Subcontractor',
                                   help="Check this box if this contact is a subcontractor. It can be selected in subcontract orders.")
    property_supplier_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
                                                        string='Subcontractor Payment Terms',
                                                        help="This payment term will be used instead of the default one for subcontract orders and progress Invoices",
                                                        )
    property_subcontract_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency", company_dependent=True,
        help="This currency will be used, instead of the default one, for subcontracts from the current partner")
    subcontract_order_count = fields.Integer(compute='_compute_subcontract_order_count',
                                             string='Subcontract Order Count')
    subcontract_supplier_invoice_count = fields.Integer(compute='_compute_subcontract_supplier_invoice_count',
                                                        string='# Progress Invoice')
    subcontract_warn = fields.Selection(WARNING_MESSAGE, 'Subcontract Order', help=WARNING_HELP, default="no-message")
    subcontract_warn_msg = fields.Text('Message for Subcontract Order')
