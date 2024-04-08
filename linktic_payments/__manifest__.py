# -*- coding: utf-8 -*-
{
    "name": "Linktic Payments",
    'summary': 'Linktic Payments Customization',
    "version": "15.1.0.0",
    'description': """
        15.0.2.2 Error correction.
        15.1.0.0 Added batch payment support.
    """,
    'category': 'Accounting/Accounting',
    "author": "Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    "license": "AGPL-3",
    "depends": ["account",
                "purchase",
                "l10n_co",
                "l10n_co_edi_jorels",
                ],

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/account_batch_payment_data.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views_extend.xml',
        'views/res_config_settings_views.xml',
        'views/account_payment_term_views_extend.xml',
        'views/account_batch_payments_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_line_view.xml',
        'views/card_movement_records_views.xml',
        'views/aws_billing_records_views.xml',
        'wizard/account_payment_register_views.xml',
        'wizard/account_payment_scheduler_views.xml',
        'wizard/account_payment_priority_views.xml',
        'wizard/account_payment_method_wizard_views.xml',
    ],

    'installable': True,
    'application': True,
}
