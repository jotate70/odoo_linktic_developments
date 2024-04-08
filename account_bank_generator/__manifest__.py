# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Desarrollador y Consultor Odoo
# linkedin: https://www.linkedin.com/in/jotate70/
# Email: jotate70@gmail.com
# Github: jotate70
# Cel. +57 3147754740

{
    'name': "Batch Payment Generator",

    'summary': """
        It allows to generate TXT file to upload the payment to the banking portal""",

    'description': """
        It allows to generate TXT file to upload the payment to the banking portal
    """,

    'author': "Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://www.todoo.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': ['linktic_payments', 'l10n_latam_base', 'report_xlsx', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/reports_xlsx.xml',
        'views/res_bank_txt_config_views.xml',
        'views/account_batch_payment_views.xml',
        'views/payment_type_views.xml',
        'views/res_partner_bank_view.xml',
        'views/res_partner_extend_view.xml',
        'views/res_partner_type_bank_account.xml',
        'wizards/payment_txt_generator_wizard_views.xml',
    ],

    'installable': True,
    'application': True,
}
