from odoo import fields, models
class HelpdeskTicketTag(models.Model):
    _name = "helpdesk.ticket.type"
    _description = "Helpdesk Ticket Tag"

    name = fields.Char()
    active = fields.Boolean(default=True)
    code = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(comodel_name='res.users', string='Assign to')
    description = fields.Text(string='Description')

    # Level Constraints of SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The type already exists'),
    ]
