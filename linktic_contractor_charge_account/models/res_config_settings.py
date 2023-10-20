from odoo import models, fields, api
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contractor_charge_default_journal_ids = fields.Many2many(comodel_name='account.journal', string='Account Journals',
                                                             help='Journals used on Contractor Charge Accounts',
                                                             related='company_id.contractor_charge_default_journal_ids',
                                                             default_model="res.company",
                                                             domain="[('type', '=', 'purchase')]",
                                                             readonly=False)
    contractor_charge_default_journal = fields.Many2one('account.journal', string='Default Account Journal',
                                                        help='Default Journal used on Contractor Charge Accounts',
                                                        related='company_id.contractor_charge_default_journal',
                                                        default_model="res.company",
                                                        domain="[('type', '=', 'purchase')]",
                                                        readonly=False)
    contractor_charge_product_id = fields.Many2one('product.product', string='Default Product',
                                                   help='Product Used on Bills created in this process',
                                                   related='company_id.contractor_charge_product_id',
                                                   default_model="res.company",
                                                   readonly=False)
    contactor_budget_approver = fields.Many2one('res.users', string='Default Contractor Budget Approver',
                                                help='User that will be assigned with the activity of budget approval',
                                                related='company_id.contactor_budget_approver',
                                                default_model="res.company",
                                                readonly=False)


