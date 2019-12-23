# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Subcontract Stock',
    'version': '1.2',
    'category': 'Subcontract',
    'sequence': 60,
    'summary': 'Subcontract Orders, Receipts, progress invoice for Stock',
    'description': "",
    'depends': ['stock_account', 'subcontract'],
    'data': [
        'security/ir.model.access.csv',
        'data/subcontract_stock_data.xml',
        'data/mail_data.xml',
        'views/subcontract_views.xml',
        'views/stock_views.xml',
        'views/stock_rule_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_production_lot_views.xml',
        'report/subcontract_report_views.xml',
        'report/subcontract_report_templates.xml',
        'report/report_stock_rule.xml',
    ],
    'demo': [
        'data/subcontract_stock_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'post_init_hook': '_create_buy_rules',
}
