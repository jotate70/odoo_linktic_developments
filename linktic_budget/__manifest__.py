# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Budget Customization",
    'summary': 'Customization to Budget module',
    "version": "15.0.1.0.0",
    'category': 'Accounting',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["om_account_budget", "l10n_co", "hr"],

    'data': [
        'security/ir.model.access.csv',
        'views/account_budget_views.xml',
        'views/account_move_views.xml',
        'views/analytic_account_views.xml',
        'views/project_views.xml',
        'views/hr_job_views.xml',
        'views/product_template_views.xml',
    ],
}
