# -*- coding: utf-8 -*-
{
    'name': "payment_cheque",

    'summary': """
        accounting>>sales>>cheques : in,,, accounting>>purchases>>cheques: out""",

    'description': """
        accounting>>sales>>cheques : in,,, accounting>>purchases>>cheques: out
    """,

    'author': "Digizilla",
    'website': "http://www.digizilla.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','account_batch_payment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/cheque_status_history.xml',
        'views/cheque_report.xml',
        'views/templates.xml',
        'views/cheque_setting_domain.xml',
        'views/payment_inherit.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    "application": False,

}
