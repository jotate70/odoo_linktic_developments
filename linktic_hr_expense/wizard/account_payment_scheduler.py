# -*- coding: utf-8 -*-

from odoo import fields, _, models, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.scheduler'
    _description = 'Scheduler for bill payments'

    hr_expense_advance_related_id = fields.Many2one(comodel_name='hr.expense.advance', string='Expense Advance')

    def action_schedule_payments(self):
        res = super().action_schedule_payments()
        for rec2 in self.active_move_ids:
            if rec2.check_advance == True and rec2.payment_state != 'paid':
                rec2.update({'payment_state': 'not_paid'})
        self.active_move_ids._relate_hr_expense_advance_related_id()
        return res


