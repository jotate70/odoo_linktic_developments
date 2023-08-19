# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# Desarrollador y funcional Odoo
# Github: jotate70
# Cel. +57 3147754740

{
    'name': "Linktic recruitment/promotion",

    'summary': """
        This module creates new models and fields to extend the functionality of recruitment requisition.
        """,

    'description': """
        Module that extends functionality in the helpdesk module and add website tickets form
        15.0.1
    """,

    'author': "Company: Andirent SAS, Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://www.andirent.co",

    'category': 'Human Resources/Employees',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'web_domain_field',
        'hr',
        'hr_recruitment',
        'hr_contract',
        'linktic_hr',
        'linktic_budget',
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
        'wizard/helpdesk_ticket_stage_transition_wizard_views.xml',
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
