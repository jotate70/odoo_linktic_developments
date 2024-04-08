from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    from_expense_advance = fields.Boolean(string='From expense advance', default=False)
    # hr_expense_advance_id = fields.Many2one(comodel_name='hr.expense.advance', string='Expense Advance')

    def cancel_expense_advance_button(self):
        """new method that will replace the normal cancel wizard button only for expense advance"""
        account_moves = self.env['account.move'].browse(self._context.get('active_ids'))

        for move in account_moves:
            move.button_draft()

    def action_create_payments(self):
        """Extend to change the state value of the expense advances to to_pay"""
        res = super(AccountPaymentRegister, self).action_create_payments()
        account_moves2 = self.env['account.move'].browse(self._context.get('active_ids'))
        for payment in self:
            for payment2 in account_moves2:
                if payment2.check_advance and payment2.approved_manager == True:
                    payment2.update({'payment_state': 'paid'})
                    payment2.hr_expense_advance_related_id._compute_onchange_state()
        return res
