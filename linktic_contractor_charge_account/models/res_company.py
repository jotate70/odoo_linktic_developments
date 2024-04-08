from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    contractor_charge_default_journal_ids = fields.Many2many(comodel_name='account.journal', string='Account Journals',
                                                             domain="[('type', '=', 'purchase')]")
    contractor_charge_default_journal = fields.Many2one('account.journal', string='Default Account Journal',
                                                        domain="[('type', '=', 'purchase')]")
    contractor_charge_product_id = fields.Many2one('product.product', string='Default Product')
    contactor_budget_approver = fields.Many2one('res.users', string="Default Contractor Budget Approver",
                                                domain=[('share', '=', False)])
    
    bonus_charge_default_journal_id = fields.Many2one('account.journal', string='Default Account Journal',
                                                      domain="[('type', '=', 'purchase')]")
    
    financial_lead_approver_id = fields.Many2one('res.users', string="Financial Lead Approver",
                                                domain=[('share', '=', False)])
    
    approver_th_id = fields.Many2one('res.users', string="Human talent approver",
                                                domain=[('share', '=', False)])
    
    vice_president_approver_id = fields.Many2one('res.users', string="Vice President Approver",
                                                domain=[('share', '=', False)])
    
    accounting_approver_id = fields.Many2one('res.users', string="accounting approver",
                                                domain=[('share', '=', False)])
    
    bonus_charge_product_id = fields.Many2one('product.product', string='Default Product')
    
    bonus_account_default_id = fields.Many2one('account.account',string="Account Default")

