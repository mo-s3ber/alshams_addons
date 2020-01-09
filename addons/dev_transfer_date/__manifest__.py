# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    'name': 'Stock Transfer Back Date & Remarks',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Warehouse',
    'summary': 'odoo App will help to set Stock Transfer Back date and remarks while doing stock Tranfer',
    'description': """
        odoo App will help to set Stock Transfer Back date and remarks while doing stock Tranfer
        Tranfer Date, back Date, Fource Dates, Stock Tranfer Date, Account move date, Date tranfer 
Stock Transfer Back Date & Remarks
Stock Transfer Back Date & Remarks 
For Helping while stock Transfer with Date and Remark
put custom back date and remarks
odoo put custom back date and remarks
Custom back date will be transfer to stock entries and accounting entries 
Odoo Custom back date will be transfer to stock entries and accounting entries 
Custom back date and remarks
Odoo custom back date and remarks
Odoo stock transfer back date & remarks
Stock transfer back date
Odoo stock transfer back date
Stock transfer remarks 
Odoo stock transfer remarks
Validate Transfer stock picking Add transfer back date and remarks
Odoo Validate Transfer stock picking Add transfer back date and remarks
Stock transfer
Odoo stock transfer
Internal stock transfer
Odoo internal stock transfer
Stock Transfer Restrict
Odoo Stock Transfer Restrict   
Stock foruce date 
tranfer fource date         
        
    """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'depends': ['stock_account', 'sale_stock',],
    'data': [
        'wizard/stock_immediate_transfer.xml',
        'views/stock_move.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':35.0,
    'currency':'EUR',
#    'live_test_url':'https://youtu.be/A5kEBboAh_k',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
