# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Project Employee Assignation",
    'summary': 'Assign Employees to different projects with the occupation percentage for each project.',
    "version": "15.0.1.0.0",
    'category': 'Services/Project',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["project", "hr"],

    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/hr_employee_views.xml',
    ],
}
