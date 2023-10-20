from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    from_expense_advance = fields.Boolean(string='From expense advance', default=False)

    def cancel_expense_advance_button(self):
        """new method that will replace the normal cancel wizard button only for expense advance"""
        account_moves = self.env['account.move'].browse(self._context.get('active_ids'))

        for move in account_moves:
            move.button_draft()

    def action_create_payments(self):
        """Extend to change the state value of the expense advances to to_pay"""
        res = super(AccountPaymentRegister, self).action_create_payments()
        for payment in self:
            if payment.from_expense_advance:
                advances = self.env['hr.expense.advance'].browse(self._context.get('expense_advances_ids'))
                advances.state = 'to_pay'
        return res
