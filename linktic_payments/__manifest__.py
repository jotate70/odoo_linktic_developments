{
    "name": "Linktic Payments",
    'summary': 'Linktic Payments Customization',
    "version": "15.0.2.0.0",
    'category': 'Accounting/Accounting',
    "author": "Omar Amaya, Update by: Julián Toscano",
    "license": "AGPL-3",
    "depends": ["account",
                "purchase"],

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views_extend.xml',
        'wizard/account_payment_register_views.xml',
        'wizard/account_payment_scheduler_views.xml',
        'wizard/account_payment_priority_views.xml',
    ],

    'installable': True,
    'application': True,
}
