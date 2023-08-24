# -*- coding: utf-8 -*-
from odoo import api, fields, models
from random import randint

class RecruitmentRequisition(models.Model):
    _name = 'hr_requisition_state'
    _description = "Recruitment Requisition Stage"
    _order = "sequence, id"

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color', default=_get_default_color)
    sequence = fields.Integer(default=1)
    name = fields.Char(string="Stage Name", required=True, translate=True)
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, default='no', required=True)
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approver',
                                 help='Responsible for approval.')
    optional_manager_id = fields.Many2one(comodel_name='hr.employee', string='Optional approver',
                                       help='Responsible for optional approval.')
    fold = fields.Boolean(string="Folded in Kanban",
                          help="This stage is folded in the kanban view when there are no records in that stage to display.")
    mail_template_id = fields.Many2one(comodel_name="mail.template", string="Email Template",
                                       domain=[("model", "=", "helpdesk.ticket")],
                                       help="If set an email will be sent to the customer when the ticket reaches this step.")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=lambda self: self.env.company)
    recruitment_type_id = fields.Many2many(comodel_name='hr_recruitment_type', relation='x_hr_recruitment_stage_rel',
                                column1='recruitment_state_id', column2='recruitment_type_id', string='Recruitment Type',
                                help='Match the stages with the types of personnel request.')
    state_type = fields.Selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('in_progress', 'In Progress'),
                                   ('recruitment', 'Recruitment'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, default='in_progress', required=True,
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    description = fields.Html(translate=True, sanitize_style=True)

    # Reset approvers
    @api.onchange('requires_approval')
    def _reset_manager_id(self):
        if self.requires_approval == 'no':
            self.manager_id = False
            self.optional_manager_id = False

    @api.onchange("closed")
    def _onchange_closed(self):
        if not self.closed:
            self.close_from_portal = False
