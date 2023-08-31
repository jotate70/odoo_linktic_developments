from odoo import fields, models, api, _
from datetime import datetime

class HrApplicantStageLog(models.Model):
    _name = "hr_applicant_stage_log"
    _description = "Applicant Stage Log"

    hr_applicant_id = fields.Many2one(comodel_name='hr.applicant', string='Applicant')
    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition", string="Recruitment Requisition")
    stage_id = fields.Many2one(comodel_name="hr.recruitment.stage", string="Order Stage", ondelete='restrict')
    user_id = fields.Many2one(comodel_name="res.users", string="Manager_id")
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')
    current_time = fields.Float(string='Current Time', store=False)


