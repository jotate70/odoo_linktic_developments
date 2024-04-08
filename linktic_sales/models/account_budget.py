from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBudgetPost(models.Model):
    _inherit = "account.budget.post"

    @api.model
    def update_initial_budget_accounts(self):
        initial_budget = self.env.ref('linktic_sales.initial_budget_post')
        accounts_used_budget = self.env['account.budget.post'].sudo().search([]).mapped('account_ids')
        initial_budget.account_ids = [(6, 0, list(set(accounts_used_budget.ids)))]
