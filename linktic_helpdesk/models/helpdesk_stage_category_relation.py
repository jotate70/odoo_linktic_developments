from odoo import fields, models, api, _
from datetime import datetime


class HelpdeskTicketStageLog(models.Model):
    _name = "helpdesk.stage.category.relation"
    _description = "Helpdesk Stage Category Relation"

    stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Helpdesk Stage", ondelete='restrict')
    category_id = fields.Many2one(comodel_name="helpdesk.ticket.category", string="Category", ondelete='restrict')
    sequence = fields.Integer(string='Sequence', default=1)
    approver_user_ids = fields.Many2many('res.users', string="Approver Users",
                                         help='Users that makes validation or approval processes on the stage')
