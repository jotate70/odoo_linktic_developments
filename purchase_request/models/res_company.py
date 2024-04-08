from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    need_contract_purchase_amount = fields.Float(string='Purchase Amount that needs Contract Files')
    need_policy_purchase_amount = fields.Float(string='Purchase Amount that needs Policy Files')
    purchase_request_approver = fields.Many2one('res.users', string="Default Request Approver",
                                                domain=[('share', '=', False)])
    purchase_quotations_manager = fields.Many2one('res.users', string="Default Quotation Manager",
                                                  domain=[('share', '=', False)])
    purchase_quotations_approver = fields.Many2one('res.users', string="Default Quotation Approver",
                                                   domain=[('share', '=', False)])
    policy_quotations_approver = fields.Many2one('res.users', string="Default Policy Purchase Order Approver",
                                                 domain=[('share', '=', False)])
    policy_max_amount_approval = fields.Float(string='Policy Amount for Approval')
    purchase_credit_card = fields.Many2one('account.journal', string="Default Credit Card for Purchases")
    analytic_account_policy = fields.Many2one('account.analytic.account',
                                              string="Default Analytic Account Policy Purchase Order")
