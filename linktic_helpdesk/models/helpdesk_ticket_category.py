from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    helpdesk_team = fields.Many2many(comodel_name="helpdesk.ticket.team", string="Helpdesk Team")
    activity_type = fields.Selection(
        selection=[('hr_recruitment', 'Employee Recruitment'), ('update_contract', 'Update Contract Info'),
                   ('other', 'Other')]
        , string="Activity Type", tracking=True, copy=False)
    stage_relation_ids = fields.One2many(comodel_name="helpdesk.stage.category.relation",
                                         inverse_name="category_id",
                                         string="Stage Process Flow")
