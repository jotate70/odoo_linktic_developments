# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Desarrollador y Consultor Odoo
# linkedin: https://www.linkedin.com/in/jotate70/
# Email: jotate70@gmail.com
# Github: jotate70
# Cel. +57 3147754740

{
    'name': "Linktic recruitment/promotion",

    'summary': """
        Selection and hiring module and modification of working conditions.
        """,

    'description': """
        15.0.1 Selection and hiring module and modification of working conditions.
    """,

    'author': "Company: Linktic, Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://linktic.com",

    'category': 'Human Resources/Employees',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'web_domain_field',
        'hr',
        'hr_recruitment',
        'hr_contract',
        'linktic_hr',       # Modificar para Odoo enterprise
        'linktic_budget',   # Reemplazar por account_budget para Odoo enterprise
    ],

    # always loaded
    'data': [
        'security/hr_recruitment_requisition_security.xml',
        'security/ir.model.access.csv',
        'data/hr_recruiment_requisition_data.xml',
        'views/hr_recruitment_requisition_views.xml',
        'views/hr_recruitment_type_views.xml',
        'views/hr_recruitment_requisition_sequence.xml',
        'views/hr_job_extend_views.xml',
        'views/hr_applicant_extend_view.xml',
        'views/hr_requisition_stage_views.xml',
        'views/hr_employee_extend_views.xml',
        'views/hr_recruitment_requisition_line_views.xml',
        'wizard/helpdesk_ticket_stage_transition_wizard_views.xml',
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
