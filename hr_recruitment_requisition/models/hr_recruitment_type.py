# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RecruitmentRequisition(models.Model):
    _name = 'hr_recruitment_type'
    _description = "Recruitment Type"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(string='Recruitment Type', required=True, translate=True)
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions'),
                                         ('2', 'Labor dismissal'),
                                         ('3', 'Disciplinary Process')],
                                        string=r'Recruitment Type', default='0', index=True, required=True)
    requisition_type = fields.Selection([('single_requisition', 'Single Requisition'),
                                         ('multiple_requisition', 'Multiple Requisition')],
                                        string=r'Requisition Type', default='single_requisition', index=True)
    state_id = fields.Many2many(comodel_name='hr_requisition_state', relation='x_hr_recruitment_stage_rel',
                                column1='recruitment_type_id', column2='recruitment_state_id', string='Stages',
                                help='List the visible stages for this type of personnel request.')
    stage_id = fields.Many2many(comodel_name='hr.recruitment.stage', relation='x_hr_recruitment_stage',
                                column1='recruitment_type_id', column2='recruitment_stage_id',
                                string='Recruitment Stage',
                                help='Match the stages with the types of personnel request.')
    resource_calendar_id = fields.Many2one(comodel_name='resource.calendar', string='Working Hours',
                                           default=lambda self: self.env.company.resource_calendar_id,
                                           domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                           help="Working hours used to determine the deadline of SLA Policies.")
    description = fields.Html(string='Description', translate=True, sanitize_style=True)

    # Stage reset
    @api.onchange('recruitment_type')
    def _reset_stage_id(self):
        self.stage_id = False




