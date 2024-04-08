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
    
    #bonus
    
    bonus_charge_default_journal_id = fields.Many2one('account.journal', string='Default journal used in Bonuses',
                                                        help='Default journal used in Bonuses',
                                                        related='company_id.bonus_charge_default_journal_id',
                                                        default_model="res.company",
                                                        domain="[('type', '=', 'purchase'),('company_id', '=', 'company_id')]",
                                                        readonly=False)
    
    financial_lead_approver_id = fields.Many2one('res.users', string='Finance Approver User',
                                                related='company_id.financial_lead_approver_id',
                                                default_model="res.company",
                                                readonly=False)
    
    approver_th_id = fields.Many2one('res.users', string='Human talent approver user',
                                                related='company_id.approver_th_id',
                                                default_model="res.company",
                                                readonly=False)
    
    vice_president_approver_id = fields.Many2one('res.users', string='Vice President Approving User',
                                                related='company_id.vice_president_approver_id',
                                                default_model="res.company",
                                                readonly=False)
    
    accounting_approver_id = fields.Many2one('res.users', string='Accounting Approver User',
                                                related='company_id.accounting_approver_id',
                                                default_model="res.company",
                                                readonly=False)
    
    bonus_charge_product_id = fields.Many2one('product.product', string='Default Product',
                                                   help='Product Used on Bills created in this process',
                                                   related='company_id.bonus_charge_product_id',
                                                   default_model="res.company",
                                                   readonly=False)
    
    bonus_account_default_id = fields.Many2one('account.account',string="Account Default",
                                               domain="[('company_id', '=', 'company_id')]",
                                               related='company_id.bonus_account_default_id',
                                               readonly=False)