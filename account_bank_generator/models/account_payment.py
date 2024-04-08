from odoo import fields, _, models, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_type_id = fields.Many2one(comodel_name='payment.type', string="Payment type")
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')
    type_bank_account_id = fields.Many2one(comodel_name='res_partner_type_bank', string='Type bank account')
    acc_number = fields.Char(string='Account Number')

    def _compute_payment_type_id(self):
        for rec in self:
            rec.payment_type_id = rec.batch_payment_id.payment_type_id
        for rec in self.partner_id.bank_ids:
            self.bank_id = rec.bank_id
            self.type_bank_account_id = rec.type_bank_account_id
            self.acc_number = rec.acc_number

