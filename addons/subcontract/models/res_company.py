from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    co_lead = fields.Float(string='Subcontract Lead Time', required=True,
                           help="Margin of error for subcontractor lead times. When the system "
                                "generates Subcontract Orders for procuring products, "
                                "they will be scheduled that many days earlier "
                                "to cope with unexpected Subcontractor delays.", default=0.0)

    co_lock = fields.Selection([
        ('edit', 'Allow to edit Subcontract orders'),
        ('lock', 'Confirmed Subcontract orders are not editable')
    ], string="Subcontract Order Modification", default="edit",
        help='Subcontract Order Modification used when you want to Subcontract order editable after confirm')

    co_double_validation = fields.Selection([
        ('one_step', 'Confirm Subcontract orders in one step'),
        ('two_step', 'Get 2 levels of approvals to confirm a Subcontract order')
    ], string="Levels of Approvals", default='one_step',
        help="Provide a double validation mechanism for Subcontracts")

    co_double_validation_amount = fields.Monetary(string='Double validation amount', default=5000,
                                                  help="Minimum amount for which a double validation is required")
