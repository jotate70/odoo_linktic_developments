# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic HR Expense Customization",
    'summary': 'Customization to HR Expense module',
    "version": "15.0.1.0.0",
    'category': 'Human Resources/Employees',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["hr_expense", 'mail'],

    'data': [
        'data/hr_expense_advance_sequence.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_expense_advance_views.xml',
        'views/hr_expense_views.xml',
        'wizard/account_payment_register_views.xml',
    ],
}
