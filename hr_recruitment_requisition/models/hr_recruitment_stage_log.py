from odoo import fields, models, api, _
from datetime import datetime

class HrRecruitmentRequisitionTicketStageLog(models.Model):
    _name = "hr_recruitment_stage_log"
    _description = "Recruitment Stage Log"

    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition", string="Recruitment Requisition", ondelete='cascade')
    stage_id = fields.Many2one(comodel_name="hr_requisition_state", string="Order Stage", ondelete='restrict')
    user_id = fields.Many2one(comodel_name="res.users", string="Manager_id")
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')
    current_time = fields.Float(string='Current Time', store=False)


