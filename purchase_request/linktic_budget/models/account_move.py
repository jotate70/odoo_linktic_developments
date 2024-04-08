from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    budget_line_segregation_id = fields.Many2one('crossovered.budget.lines.segregation',
                                                 string='Budget Line Segregation',
                                                 copy=False)

    def _prepare_analytic_line(self):
        """ override to add new budget line segregation id field"""
        values_list = super(AccountMoveLine, self)._prepare_analytic_line()
        for line_move in self:
            line_dic = next((item for item in values_list if item["move_id"] == line_move.id), None)
            if line_dic:
                line_dic['budget_line_segregation_id'] = line_move.budget_line_segregation_id.id
        return values_list
