# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_bank_account = fields.Selection(selection=[('payroll_account', 'payroll account'),
                                                    ('savings_account', 'Savings account'),
                                                    ('current_account', 'Current account'),
                                                    ('express_account', 'Express account'),
                                                    ('CDT', 'Certificates of deposit or CDT'),
                                                    ('pension_account', 'Pension account')],
                                         string='Type bank account',
                                         store=True,
                                         default='payroll_account')



