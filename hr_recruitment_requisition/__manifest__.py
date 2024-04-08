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
        15.0.0 Selection and hiring module and modification of working conditions.
        15.1.0 New fields are added, in HR ticket and in applications.
        15.1.1 Error correction.
        15.1.2 sequences correction and assignee notification.
        15.2.0 Conditions are added for the duration of the contract, the type of contract.
    """,

    'author': "Company: Linktic, Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://linktic.com",

    'category': 'Human Resources/Employees',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web_domain_field',
        'hr',
        'hr_recruitment',
        'hr_contract',
        'l10n_latam_base',
        'account',
        'contacts',
        'om_hr_payroll_account', # Modificar para Odoo enterprise
        'linktic_hr',       # Modificar para Odoo enterprise
        'linktic_budget',   # Reemplazar por account_budget para Odoo enterprise
    ],

    # always loaded
    'data': [
        # 'data/hr_recruitment_requisition_sequence.xml',
        # 'data/hr_recruiment_requisition_data.xml',
        'security/hr_recruitment_groups_security.xml',
        'security/hr_recruitment_rule_security.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/hr_recruitment_requisition_views.xml',
        'views/hr_recruitment_type_views.xml',
        # 'views/hr_job_extend_views.xml',
        'views/hr_applicant_extend_view.xml',
        'views/hr_requisition_stage_views.xml',
        'views/hr_recruitment_stage_extend_views.xml',
        'views/hr_recruitment_stage_extend_views.xml',
        'views/discipline_reason_category.xml',
        'views/hr_employee_views_extend.xml',
        'wizard/hr_recruitment_requisition_stage_transition_wizard_views.xml',
        'wizard/hr_applicant_stage_transition_wizard_views.xml',
        'wizard/applicant_refuse_reason_views_extend.xml',
        'views/contract_management_setting.xml',
        'views/contract_management_line.xml',
        'views/hr_hiring_time_views.xml',
        'views/hr_contract_type_extend_view.xml',
        'views/hr_recruitment_requisition__menus_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_recruitment_requisition/static/src/js/hr_contract_reference.js',
        ],
    },
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
