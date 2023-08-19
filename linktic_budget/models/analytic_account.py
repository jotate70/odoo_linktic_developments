from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    budget_line_segregation_id = fields.Many2one('crossovered.budget.lines.segregation',
                                                 'Budget Line Segregation', copy=False)
