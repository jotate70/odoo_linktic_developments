# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Linktic HR Customization",
    'summary': 'Customization to HR module',
    "version": "15.0.1.0.0",
    'category': 'Human Resources/Employees',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["hr_recruitment", "hr_holidays", "l10n_latam_base", "om_hr_payroll"],

    'data': [
        'data/res_partner_data.xml',
        'data/hr_payroll_parameter.xml',
        'data/l10n_latam_identification_type_data.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_recruitment_views.xml',
        'views/hr_parameter_views.xml',
        'views/hr_employee_arl_risk_views.xml',
        'wizard/hr_employee_certifications_views.xml',
        'report/paperformat.xml',
        'report/templates.xml',
        'report/hr_employee_certification.xml',
    ],
}

