from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    hr_expense_advance_account = fields.Many2one('account.account', string='Expense Advance Account')
    hr_expense_advance_gain_account = fields.Many2one('account.account', string='Expense Advance Gain Account')
    hr_expense_advance_loss_account = fields.Many2one('account.account', string='Expense Advance Loss Account')
