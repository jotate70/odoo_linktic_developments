# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic HR Expense Customization",
    'summary': 'Customization to HR Expense module',
    "version": "15.0.2.1.0",
    'category': 'Human Resources/Employees',
    "author": "Author: Julián Toscano, https://www.linkedin.com/in/jotate70/o",
    "license": "AGPL-3",
    "depends": ['hr_expense',
                'account',
                'mail',
                'linktic_payments',
                ],

    'data': [
        'data/hr_expense_advance_sequence.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_expense_advance_views.xml',
        'views/hr_expense_views.xml',
        'views/res_partner_views_extend.xml',
        'views/account_move_views_extend.xml',
        'wizard/account_payment_register_views.xml',
    ],

    'installable': True,
    'application': True,
}
