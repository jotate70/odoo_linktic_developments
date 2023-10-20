from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    hr_contractor_charge_account_id = fields.Many2one(string="Contractor Charge Account",
                                                      comodel_name="hr.contractor.charge.account")

    def button_cancel(self):
        for move in self:
            if move.hr_contractor_charge_account_id:
                move.hr_contractor_charge_account_id.state = 'rejected'
        return super(AccountMove, self).button_cancel()
