from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_expense_advance_account = fields.Many2one('account.account', string='Initial Account',
                                                 help='Account used in the Expense Advance entries',
                                                 related='company_id.hr_expense_advance_account', readonly=False)
    hr_expense_advance_gain_account = fields.Many2one('account.account', string='Gain Account',
                                                      help='Account used when the summation of expenses is lower than the advance',
                                                      related='company_id.hr_expense_advance_gain_account',
                                                      readonly=False)
    hr_expense_advance_loss_account = fields.Many2one('account.account', string='Loss Account',
                                                      help='Account used when the summation of expenses is greater than the advance',
                                                      related='company_id.hr_expense_advance_loss_account',
                                                      readonly=False)