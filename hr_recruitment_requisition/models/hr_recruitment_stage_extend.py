# -*- coding: utf-8 -*-
from odoo import api, fields, models
from random import randint

class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'
    _description = "Recruitment Stages"
    _order = 'sequence'

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color', default=_get_default_color)
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, default='no', required=True)
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approver',
                                 help='Responsible for approval.')
    optional_manager_id = fields.Many2one(comodel_name='hr.employee', string='Optional approver',
                                       help='Responsible for optional approval.')
    recruitment_type_id = fields.Many2many(comodel_name='hr_recruitment_type', relation='x_hr_recruitment_stage',
                                column1='recruitment_stage_id', column2='recruitment_type_id', string='Recruitment Type',
                                help='Match the stages with the types of personnel request.')
    requires_budget_approval = fields.Boolean(string='Requires budget approval')
    budget_amount = fields.Monetary(string='Budget amount', help='maximum amount you can approve.')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    uncapped_manager_id = fields.Many2one(comodel_name='hr.employee', string='Uncapped manager',
                                       help='responsible for the stage that does not have a limit on the amount to be approved.')

    @api.onchange('requires_approval')
    def _reset_requires_approval(self):
        self.manager_id = False
        self.optional_manager_id = False
        self.requires_budget_approval = False

    @api.onchange('requires_budget_approval')
    def _reset_requires_budget_approval(self):
        self.budget_amount = False
        self.uncapped_manager_id = False