# -*- coding: utf-8 -*-
{
    'name': "subcontract_requisition",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jothimani R / Jerv Soft Solutions",
    'website': "http://jervsoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock', 'subcontract', 'subcontract_stock'],

    # always loaded
    'data': [
        'security/subcontract_tender.xml',
        'security/ir.model.access.csv',
        'data/purchase_requisition_data.xml',
        'views/views.xml',
        'report/subcontract_requisition_report.xml',
        'report/report_subcontractrequisition.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
