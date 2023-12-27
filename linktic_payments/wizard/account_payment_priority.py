# -*- coding: utf-8 -*-

from odoo import fields, _, models, api

class AccountPaymentRegister(models.TransientModel):
    _name = 'account.payment.priority'

    account_move_ids = fields.Many2many(comodel_name='account.move', string='Account Move')
    priority = fields.Selection(selection=[('0', 'All'),
                                           ('1', 'Low priority'),
                                           ('2', 'High priority'),
                                           ('3', 'Urgent')],
                                string='Priority', tracking=True,
                                default='0', index=True)

    def do_action(self):
        for rec in self.account_move_ids:
            rec._compute_select_priority(self.priority)



