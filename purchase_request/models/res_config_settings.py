from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    need_contract_purchase_amount = fields.Float(string='Purchase Amount',
                                                 help='Purchase Amount that needs Contract Files',
                                                 related='company_id.need_contract_purchase_amount', readonly=False)
    need_policy_purchase_amount = fields.Float(string='Policy Amount', help='Purchase Amount that needs Policy Files',
                                               related='company_id.need_policy_purchase_amount', readonly=False)
    purchase_request_approver = fields.Many2one('res.users', string='Default Request Approver',
                                                help='User that will be assigned with the activity of request approval',
                                                related='company_id.purchase_request_approver',
                                                default_model="res.company",
                                                readonly=False)
    purchase_quotations_manager = fields.Many2one('res.users', string='Default Quotation Manager',
                                                  help='User that will be assigned with the activity of quotation creation',
                                                  related='company_id.purchase_quotations_manager',
                                                  default_model="res.company",
                                                  readonly=False)
    purchase_quotations_approver = fields.Many2one('res.users', string='Default Quotation Approver',
                                                   help='User that will be assigned with the activity of quotation approval',
                                                   related='company_id.purchase_quotations_approver',
                                                   default_model="res.company",
                                                   readonly=False)
    policy_quotations_approver = fields.Many2one('res.users', string='Default Policy Purchase Order Approver',
                                                 help='User that will be assigned with the activity of policy quotation approval',
                                                 related='company_id.policy_quotations_approver',
                                                 default_model="res.company",
                                                 readonly=False)
    policy_max_amount_approval = fields.Float(string='Policy Amount for Approval',
                                              help='Max. quotation amount that will manage the policy quotation approver',
                                              related='company_id.policy_max_amount_approval', readonly=False)
    purchase_credit_card = fields.Many2one('account.journal', string='Default Credit Card for Purchases',
                                           related='company_id.purchase_credit_card',
                                           default_model="res.company",
                                           readonly=False)
    analytic_account_policy = fields.Many2one('account.analytic.account',
                                              string='Default Analytic Account Policy Purchase Order',
                                              related='company_id.analytic_account_policy',
                                              default_model="res.company",
                                              readonly=False)
