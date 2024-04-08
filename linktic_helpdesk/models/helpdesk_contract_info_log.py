from odoo import fields, models, api, _
from datetime import datetime


class HelpdeskContractInfoLog(models.Model):
    _name = "helpdesk.contract.info.log"
    _description = "Ticket Contract Info Log"

    helpdesk_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Helpdesk Ticket", ondelete='cascade')
    stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Stage", ondelete='restrict')
    user_id = fields.Many2one(comodel_name="res.users", string="User")
    change_datetime = fields.Datetime(string='Change Date')
    field_name = fields.Char(string='Field Name')
    origin_value = fields.Char(string='Original Value')
    actual_value = fields.Char(string='Actual Value')
