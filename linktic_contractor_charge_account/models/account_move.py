from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    hr_contractor_charge_account_id = fields.Many2one(string="Contractor Charge Account",
                                                      comodel_name="hr.contractor.charge.account")
    
    bonuses_id = fields.Many2one(string="Bonus",comodel_name="request.bonuses")
    account_type = fields.Selection(related='hr_contractor_charge_account_id.account_type')
    
    def button_cancel(self):
        for move in self:
            if move.hr_contractor_charge_account_id:
                move.hr_contractor_charge_account_id.state = 'rejected'
            if move.bonuses_id:
                move.bonuses_id.cancel_bonus()
                if move.bonuses_id.charge_account_ids:
                    for account_id in move.bonuses_id.charge_account_ids:
                        for invoice_id in account_id.invoice_ids:
                            invoice_id.state = 'cancel'
        return super(AccountMove, self).button_cancel()
    
    @api.constrains('state')
    def move_the_bonus_to_approved_status(self):
        bonus_amount = self.env['account.move'].search([('bonuses_id', '=', self.bonuses_id.id)])
        bonus_amount_published = self.env['account.move'].search([('bonuses_id', '=', self.bonuses_id.id),('state', '=','posted')])
        if bonus_amount_published == bonus_amount:
            self.bonuses_id.request_approval()          
