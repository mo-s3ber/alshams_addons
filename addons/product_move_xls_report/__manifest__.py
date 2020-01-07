# -*- coding: utf-8 -*-
{
    'name': 'Product Move Excel',
    'version': '1.0.0',
    'category': 'Sale',
    'summary': '''
        Prints Excel Report based on Product Moves.
        ''',
    'author': 'HK',
    'license': "OPL-1",
    'depends': [
        'stock','split_journal_entry'
    ],
    'data': [
        'wizard/sale_order_xls_view.xml',
        # 'securty/ir.model.access.csv',
    ],
    'demo': [],  
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True
}
