from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "project.project"

    crossovered_budget_id = fields.Many2one("crossovered.budget", "Project Budget", compute='_get_budget_project')

    def _get_budget_project(self):
        for project in self:
            if project.analytic_account_id:
                project.crossovered_budget_id = self.env['crossovered.budget'].search(
                    [('analytic_account_id', '=', project.analytic_account_id.id)])
            else:
                project.crossovered_budget_id = False
