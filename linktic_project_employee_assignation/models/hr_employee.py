from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "hr.employee"

    project_assignation_ids = fields.One2many(string="Project Assignations",
                                               comodel_name="project.employee.assignation",
                                               inverse_name="employee_id", )
