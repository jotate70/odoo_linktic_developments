from odoo import fields, models, api, _
from datetime import datetime

class HelpdeskTicketStageLog(models.Model):
    _name = "hr_recruitment_stage_log"
    _description = "Recruitment Stage Log"

    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition", string="Recruitment Requisition", ondelete='cascade')
    stage_id = fields.Many2one(comodel_name="hr_requisition_state", string="Order Stage", ondelete='restrict')
    user_id = fields.Many2one(comodel_name="res.users", string="Manager_id")
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')
    current_log = fields.Boolean(string='Current log')
    current_time = fields.Float(string='Current Time', compute='_get_time_current_stage', store=False)

    def _get_time_current_stage(self):
        for record in self:
            working_calendar = record.hr_recruitment_requisition_id.recruitment_type_id.resource_calendar_id
            if record.current_log and record.stage_id.state_type != 'done':
            # if record.current_log and not record.stage_id.closed:
                hours = working_calendar.get_work_hours_count(record.datetime_start, datetime.now(),
                                                              compute_leaves=True)
                record.current_time = hours
            else:
                record.current_time = False

