# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    visa_country_id = fields.Many2one(comodel_name='res.country', string="País de la Visa")
    expense_manager_id2 = fields.Many2one(comodel_name='res.users', string='Expense',
                                         store=True, readonly=False, related='company_id.expense_manager_id')

    @api.depends('parent_id')
    def _compute_expense_manager(self):
        for employee in self:
            employee.expense_manager_id = employee.expense_manager_id2




