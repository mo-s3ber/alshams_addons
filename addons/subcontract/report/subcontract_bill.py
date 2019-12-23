from odoo import api, fields, models, tools
from odoo.tools import formatLang

class SubcontractBillUnion(models.Model):
    _name = 'subcontract.bill.union'
    _auto = False
    _description = 'Subcontracts & Bills Union'
    _order = "subcontract_order_id desc, progress_invoice_id desc"

    name = fields.Char(string='Reference', readonly=True)
    reference = fields.Char(string='Source', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Subcontract', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    progress_invoice_id = fields.Many2one('account.invoice', string='Progress Invoice', readonly=True)
    subcontract_order_id = fields.Many2one('purchase.order', string='Subcontract Order', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'subcontract_bill_union')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW subcontract_bill_union AS (
                SELECT
                    id, number as name, reference, partner_id, date, amount_untaxed as amount, currency_id, company_id,
                    id as progress_invoice_id, NULL as subcontract_order_id
                FROM account_invoice
                WHERE
                    type='in_invoice' and state in ('open','in_payment','paid','cancel')
            UNION
                SELECT
                    -id, name, partner_ref, partner_id, date_order::date as date, amount_untaxed as amount, currency_id, company_id,
                    NULL as progress_invoice_id, id as subcontract_order_id
                FROM subcontract_order
                WHERE
                    state = 'subcontract' AND
                    invoice_status in ('to invoice', 'no')
            )""")

    def name_get(self):
        result = []
        for doc in self:
            name = doc.name or ''
            if doc.reference:
                name += ' - ' + doc.reference
            amount = doc.amount
            if doc.subcontract_order_id and doc.subcontract_order_id.invoice_status == 'no':
                amount = 0.0
            name += ': ' + formatLang(self.env, amount, monetary=True, currency_obj=doc.currency_id)
            result.append((doc.id, name))
        return result