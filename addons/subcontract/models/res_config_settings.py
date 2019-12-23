from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lock_confirmed_co = fields.Boolean("Lock Confirmed Orders",
                                       default=lambda self: self.env.user.company_id.co_lock == 'lock')
    co_lock = fields.Selection(related='company_id.co_lock', string="Subcontract Order Modification *", readonly=False)
    co_order_approval = fields.Boolean("Subcontract Order Approval",
                                       default=lambda self: self.env.user.company_id.co_double_validation == 'two_step')
    co_double_validation = fields.Selection(related='company_id.co_double_validation', string="Levels of Approvals *",
                                            readonly=False)
    co_double_validation_amount = fields.Monetary(related='company_id.co_double_validation_amount',
                                                  string="Minimum Amount", currency_field='company_currency_id',
                                                  readonly=False)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True,
                                          help='Utility field to express amount currency')
    default_subcontract_method = fields.Selection([
        ('subcontract', 'Ordered quantities'),
        ('receive', 'Delivered quantities'),
    ], string="Bill Control", default_model="product.template",
        help="This default value is applied to any new product created. "
             "This can be changed in the product detail form.", default="receive")
    group_warning_subcontract = fields.Boolean("Subcontract Warnings",
                                               implied_group='subcontract.group_warning_subcontract')
    # todo:check group
    group_manage_subcontractor_price = fields.Boolean("Subcontractor Pricelists", implied_group = "subcontract.group_manage_subcontractor_price")
    group_manage_rfq_approval = fields.Boolean("RFQ Approval", implied_group = "subcontract.group_manage_rfq_approval")
    #
    module_account_3way_match = fields.Boolean("3-way matching: subcontracts, receptions and bills")
    module_subcontract_requisition = fields.Boolean("Contract")
    co_lead = fields.Float(related='company_id.co_lead', readonly=False)
    use_co_lead = fields.Boolean(
        string="Security Lead Time for Subcontract",
        oldname='default_new_co_lead',
        config_parameter='subcontract.use_co_lead',
        help="Margin of error for subcontractor lead times. When the system generates Subcontract Orders for reordering products,they will be scheduled that many days earlier to cope with unexpected subcontractor delays.")

    @api.onchange('use_co_lead')
    def _onchange_use_co_lead(self):
        if not self.use_co_lead:
            self.co_lead = 0.0

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.co_lock = 'lock' if self.lock_confirmed_co else 'edit'
        self.co_double_validation = 'two_step' if self.co_order_approval else 'one_step'
