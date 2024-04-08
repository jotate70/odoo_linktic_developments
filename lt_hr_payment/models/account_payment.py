from odoo import models, _, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payslip_run_id = fields.Many2one(comodel_name='hr.payslip.run')

    @api.depends('journal_id', 'payment_type', 'payment_method_line_id')
    def _compute_outstanding_account_id(self):
        super(AccountPayment, self)._compute_outstanding_account_id()

        for payment in self:
            payment.outstanding_account_id = payment.journal_id.suspense_account_id

    def _get_valid_liquidity_accounts(self):
        result = super()._get_valid_liquidity_accounts()
        return result | self.journal_id.suspense_account_id