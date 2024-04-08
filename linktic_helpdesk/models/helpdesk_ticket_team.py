from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.team"

    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours',
                                           default=lambda self: self.env.company.resource_calendar_id,
                                           domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                           help="Working hours used to determine the deadline of SLA Policies.")
