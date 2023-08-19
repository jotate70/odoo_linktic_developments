from odoo import fields, models, api, _
from datetime import datetime


class HelpdeskTicketStageLog(models.Model):
    _name = "helpdesk.ticket.stage.log"
    _description = "Ticket Stage Log"

    helpdesk_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Helpdesk Ticket", ondelete='cascade')
    stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Helpdesk Stage", ondelete='restrict')
    user_id = fields.Many2one(comodel_name="res.users", string="User")
    datetime_start = fields.Datetime(string='Start Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')
    current_log = fields.Boolean(string='Current log')
    current_time = fields.Float(string='Current Time', compute='_get_time_current_stage', store=False)

    def _get_time_current_stage(self):
        for record in self:
            working_calendar = record.helpdesk_ticket_id.team_id.resource_calendar_id
            if record.current_log and not record.stage_id.closed:
                hours = working_calendar.get_work_hours_count(record.datetime_start, datetime.now(),
                                                              compute_leaves=True)
                record.current_time = hours
            else:
                record.current_time = False

