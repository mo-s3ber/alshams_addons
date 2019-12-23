# -*- coding: utf-8 -*-
{
    'name': "subcontract",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Prabakaran R / Jerv Soft Solutions",
    'website': "http://jervsoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'data/subcontract_menus.xml',
        'security/subcontract_security.xml',
        'data/subcontract_order_template.xml',
        'data/subcontract_quotation_templates.xml',
        'data/subcontract_data.xml',
        'data/subcontract_report.xml',
        'data/mail_template_data.xml',
        'data/subcontract_template.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'report/subcontract_report_view.xml',
        'report/subcontract_bill_views.xml',
        'views/subcontract_view.xml',
        'views/res_config_settings_view.xml',

    ],
}
