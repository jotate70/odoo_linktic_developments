from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    employee_assignation_ids = fields.One2many(string="Employee Assignations",
                                               comodel_name="project.employee.assignation",
                                               inverse_name="project_id", )
