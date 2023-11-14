# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# Desarrollador y funcional Odoo
# linkedin: https://www.linkedin.com/in/jotate70/
# Github: jotate70
# Cel. +57 3147754740

{
    'name': 'Employee Travel Expense Lintick',
    'version': '2.0',
    'category': 'Human Resources/Expenses',
    'sequence': 70,
    'summary': 'Submit, validate and reinvoice employee expenses extend',
    'description': """
    This module will allow you to manage travel of your employees and expense advance and submit expense claim. 
    15.1.0
    15.2.0 Add request for travel, hotels, analytical account grouping, third party, items.
    15.2.1 Error Corrections.
    """,

    'author': "Linktic  Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': 'https://linktic.com',
    'depends': ['base',
                'hr_expense',
                'project',
                'l10n_co',
                'purchase_request',
                'linktic_hr_expense',
                ],

    'data': ['security/ir.model.access.csv',
             'views/hr_expense_views_extend.xml',
             'views/hr_expense_sheet_views_extend.xml',
             'views/travel_request_views.xml',
             'views/hr_travel_type.xml',
             'views/hr_travel_info_views.xml',
             'views/hr_hotel_info_views.xml',
             'views/product_product_extend_view.xml',
             'views/res_config_settings_extend_view.xml',
             'views/hr_employee_extend_views.xml',
             'views/hr_job_extend_views.xml',
             'views/purchase_request_view_extend.xml',
             'views/hr_expense_advance_view_extend.xml',
             'report/employee_travel_report.xml',
             'report/report_views.xml',
             'report/hr_expense_report_extend.xml',
    ],
    'installable': True,
    'application': True,
}
