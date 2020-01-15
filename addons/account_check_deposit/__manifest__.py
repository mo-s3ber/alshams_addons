# -*- coding: utf-8 -*-
# © 2012-2015 Akretion (http://www.akretion.com/)
# @author: Benoît GUILLOT <benoit.guillot@akretion.com>
# @author: Chafique DELLI <chafique.delli@akretion.com>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Check Deposit',
    'version': '11',
    'category': 'Accounting & Finance',
    'license': '',
    'summary': 'Manage deposit of checks to the bank',
    'author': "Archer Solutions",
    'website': 'http://www.archersolutions.com/',
    'depends': [
        'account_accountant','account'
    ],
    'data': [
        'data/sequence.xml',
        'views/account_deposit_view.xml',
        'views/account_move_line_view.xml',
        'views/account_config_settings.xml',
        'views/check_payment.xml',
        'views/account_journal.xml',
        'security/ir.model.access.csv',
        'security/check_deposit_security.xml',
        'report/report.xml',
        'report/report_checkdeposit.xml',
    ],
    'installable': True,
    'application': True,
}
