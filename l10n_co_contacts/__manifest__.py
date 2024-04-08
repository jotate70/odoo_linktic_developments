# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# Desarrollador y funcional Odoo
# Github: jotate70
# Cel. +57 3147754740
#
#
{
    'name': "contacts extend",

    'summary': """
        15.0.1 fields required by Sagrilaft are added.
        15.1.0 constrainst on contact field
        """,

    'description': """
        Add options and required fields for Colombian localization
        
        NOTE: sagrilaft settings are made on the sarlaft page in the contacts module
    """,

    'author': "Andirent  Author: Julián Toscano",
    'website': "https://www.andirent.co",

    'category': 'Contacts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',
        'l10n_co',
        'l10n_co_edi_jorels',
    ],

    # always loaded
    'data': [
        'views/res_partner_extend_view.xml',
        'views/res_partner_settings_view.xml',
        'views/res_partner_bank_view.xml',
    ],

    'installable': True,
    'application': True,

    # 'license': 'LGPL-3',
}
