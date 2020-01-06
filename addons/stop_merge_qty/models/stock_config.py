# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stop_merge = fields.Boolean(string='Not To Merge', related='company_id.stop_merge', readonly=False)

class ResCompany(models.Model):
    _inherit = 'res.company'

    stop_merge = fields.Boolean(string='Not To Merge' )
