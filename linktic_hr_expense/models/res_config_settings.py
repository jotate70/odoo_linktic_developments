from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_expense_advance_account = fields.Many2one(comodel_name='account.account', string='Initial Account',
                                                 help='Account used in the Expense Advance entries',
                                                 domain="[('user_type_id.type', '=', 'payable'), ('company_id', '=', company_id)]",
                                                 related='company_id.hr_expense_advance_account', readonly=False)
    hr_expense_advance_gain_account = fields.Many2one(comodel_name='account.account', string='Gain Account',
                                                      help='Account used when the summation of expenses is lower than the advance',
                                                      related='company_id.hr_expense_advance_gain_account',
                                                      domain="[('company_id', '=', company_id)]",
                                                      readonly=False)
    hr_expense_advance_loss_account = fields.Many2one(comodel_name='account.account', string='Loss Account',
                                                      help='Account used when the summation of expenses is greater than the advance',
                                                      related='company_id.hr_expense_advance_loss_account',
                                                      domain="[('company_id', '=', company_id)]",
                                                      readonly=False)
    property_account_advance_id = fields.Many2one(comodel_name='account.account', string='Cuenta para anticipo',
                                                  help='Default employee imprest account',
                                                  related='company_id.property_account_advance_id',
                                                  domain="[('company_id', '=', company_id)]",
                                                  readonly=False)
    journal_expense_advance_id = fields.Many2one(comodel_name='account.journal', string="Advance Journal",
                                                 help='Default journal expense advance',
                                                 related='company_id.journal_expense_advance_id',
                                                 domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
                                                 readonly=False)