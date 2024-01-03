# -*- coding: utf-8 -*-

from odoo import fields, _, models, api

class AccountPaymentMethodWizard(models.TransientModel):
    _name = 'account.payment.method.wizard'

    account_move_ids = fields.Many2many(comodel_name='account.move', string='Account Move')
    payment_method_line_id = fields.Many2one(comodel_name='account.payment.method.line', string='Payment Method')

    def do_action(self):
        for rec in self.account_move_ids:
            rec._compute_select_payment_method_line_id(self.payment_method_line_id)



