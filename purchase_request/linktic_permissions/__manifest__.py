# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Permissions",
    'summary': 'Change of permissions and User Groups',
    "version": "15.0.1.0.0",
    'category': 'Extra Rights',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["sale", "stock"],

    'data': [
        'security/event_security.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/res_users_views.xml',
    ],
}
