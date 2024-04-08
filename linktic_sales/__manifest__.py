# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Sales Customization",
    'summary': 'Customization to Sales module',
    "version": "15.0.1.0.0",
    'category': 'Sales/Sales',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["sale", "purchase_request"],

    'data': [
        'data/account_budget_post_data.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/crm_team_views.xml',
        'wizard/sale_order_assing_policy_views.xml',
    ],
}
