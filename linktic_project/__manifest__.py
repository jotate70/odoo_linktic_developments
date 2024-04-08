# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Project Customization",
    'summary': 'Customization to Project module',
    'description': """
                15.0.1.0.0 Customization to Project module,
                15.0.2.0.0 Planned date and timeline view support.
               """,
    "version": "15.0.2.0.0",
    'category': 'Services/Project',
    "author": "Omar Amaya, Update: Julián Toscano",
    "license": "AGPL-3",
    "depends": ['project',
                'hr_timesheet',
                'purchase_request',
                'project_timeline',
                ],

    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],

    'installable': True,
    'application': True,
}
