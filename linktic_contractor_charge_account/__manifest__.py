# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Contractor Employee Charge Accounts",
    'summary': 'Create and manages Charge Account documents related to contractors type employees.',
    "version": "15.0.2.0.0",
    'description': """
            15.0.1.0.0 Initial version.
            15.0.2.0.0 Correction to standard 30 days worked per month, add field worked days.
            """,
    'category': 'Human Resources/Employees',
    "author": "Omar Amaya, update by: Julián Toscano",
    "license": "AGPL-3",
    "depends": ["linktic_hr", "purchase_request", "base"],

    'data': [
        'data/contractor_charge_account_sequence.xml',
        'security/contractor_charge_account.xml',
        'security/ir.model.access.csv',
        'views/contractor_charge_account_views.xml',
        'views/contractor_reported_hours_views.xml',
        'views/res_config_settings_views.xml',
        'views/contractor_charge_account_line_views.xml',
        'views/account_move_views.xml',
        'views/linktic_report_task_view.xml',
        'views/request_for_bonuses.xml',
    ],

    'installable': True,
    'application': True,
}
