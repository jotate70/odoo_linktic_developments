from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    hr_expense_advance_account = fields.Many2one(comodel_name='account.account', string='Expense Advance Account',
                                                 copy=True)
    hr_expense_advance_gain_account = fields.Many2one(comodel_name='account.account', string='Expense Advance Gain Account',
                                                      copy=True)
    hr_expense_advance_loss_account = fields.Many2one(comodel_name='account.account', string='Expense Advance Loss Account',
                                                      copy=True)
    property_account_advance_id = fields.Many2one(comodel_name='account.account', string='Cuenta para anticipo',
                                                  copy=True)
    journal_expense_advance_id = fields.Many2one(comodel_name='account.journal', string="Advance Journal",
                                                 copy=True)
