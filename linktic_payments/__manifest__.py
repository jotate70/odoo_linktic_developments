# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Payments",
    'summary': 'Linktic Payments Customization',
    "version": "15.0.1.0.0",
    'category': 'Accounting/Accounting',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["account"],

    'data': [
        'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'wizard/account_payment_register_views.xml',
        'wizard/account_payment_scheduler_views.xml',
    ],
}
