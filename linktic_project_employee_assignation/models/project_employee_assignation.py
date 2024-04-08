from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare


class ProjectEmployeeAssignation(models.Model):
    _name = 'project.employee.assignation'
    _description = "Project Employee Assignation"

    project_id = fields.Many2one("project.project", string="Project", ondelete="cascade")
    employee_id = fields.Many2one("hr.employee", string="Employee", ondelete="cascade")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    occupation_perc = fields.Float(string="Occupation %")
    observations = fields.Text(string="Observations")

    @api.constrains('employee_id', 'date_start', 'date_end', 'occupation_perc')
    def _check_line_date(self):
        for line in self:
            domains = [[('date_start', '<', line.date_end), ('date_end', '>=', line.date_start)
                        , ('employee_id', '=', line.employee_id.id)]]
            domain = expression.OR(domains)

            projects_in_range = self.search(domain)
            if sum(projects_in_range.mapped('occupation_perc')) > 1:
                raise ValidationError(
                    _(f"Employee {line.employee_id.name} doesn't have the the availability in this date range."))

            if float_compare(line.occupation_perc, 0.0, precision_digits=2) <= 0:
                raise ValidationError(
                    _(f"The occupation percentage for employee {line.employee_id.name} cannot be less or equal to 0"))
