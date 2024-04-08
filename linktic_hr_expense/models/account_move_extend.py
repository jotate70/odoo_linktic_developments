from odoo import fields, _, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    hr_expense_advance_related_id = fields.Many2one(comodel_name='hr.expense.advance', string='Expense Advance')
    check_advance = fields.Boolean(string='Check Advance', store=True)

    # related approved manager in account move
    @api.onchange('approved_manager', 'scheduled_payment_day')
    def _relate_hr_expense_advance_related_id(self):
        self.write({'payment_state': 'not_paid'})
        for rec in self:
            rec.hr_expense_advance_related_id.update({'scheduled_payment_day': rec.scheduled_payment_day,
                                                      'payment_journal_id': rec.payment_journal_id.id,
                                                      'approved_manager': rec.approved_manager,
                                                      })

    def approve_bills(self):
        res = super().approve_bills()
        moves2 = self.env['account.move'].browse(self._context.get('active_ids'))
        moves2._relate_hr_expense_advance_related_id()
        return res

    def action_register_payment(self):
        res = super().action_register_payment()
        for rec in self:
            if rec.check_advance:
                # rec.write({'payment_state': 'paid'})
                rec.hr_expense_advance_related_id.update({'state': 'to_pay'})
        return res
