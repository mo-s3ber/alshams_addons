# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Inventory Valuation Per Location',
    'summary': """
        Inventory Valuation Per Location""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'website': '',
    'author': '',
    'depends': [
        'stock',
        'stock_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
    ],
}
