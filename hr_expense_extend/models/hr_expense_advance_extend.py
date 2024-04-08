from odoo import fields, _, models, api

class HrExpenseAdvance(models.Model):
    _inherit = "hr.expense.advance"
    _description = "HR Expense Advance"

    travel_request_id = fields.Many2one(comodel_name='travel.request', string='Solicitud de viaje')
    product_id = fields.Many2one(comodel_name='product.product', string="Producto",
                                 domain=[('can_be_expensed','=',True), ('product_expense_type','=','advance')])
    days = fields.Char(string='Días', related='travel_request_id.days')
    days2 = fields.Char(string='Días', related='travel_request_id.days2')
    amount_qty = fields.Monetary(string='Valor día')

    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        res = super(HrExpenseAdvance, self)._compute_select_manager_id()
        if self.travel_request_id:
            self.journal_id = self.travel_request_id.journal_travel_id
        return res

    @api.onchange('product_id', 'employee_id', 'travel_request_id')
    def _select_manager_employee_id(self):
        if self.travel_request_id:
            for rec in self:
                value = 0
                amount = rec.env['hr_type_travel_expenses'].search([('product_id', '=', rec.product_id.ids),
                                                                    ('currency_id', '=', rec.currency_id.ids)], limit=1)
                if amount:
                    if rec.employee_id.job_id.job_type == 'president':
                        value = amount.amount_president
                    elif rec.employee_id.job_id.job_type == 'vice_president':
                        value = amount.amount_vice_president
                    elif rec.employee_id.job_id.job_type == 'director':
                        value = amount.amount_director
                    elif rec.employee_id.job_id.job_type == 'department_manager':
                        value = amount.amount_department_manager
                    elif rec.employee_id.job_id.job_type == 'project_manager':
                        value = amount.amount_project_manager
                    elif rec.employee_id.job_id.job_type == 'operational_staff':
                        value = amount.amount_operational_staff
                else:
                    value = 0
                rec.amount_qty = value
                rec.total_amount = value * int(rec.days2)
                rec.analytic_account_id = rec.travel_request_id.account_analytic_id
                rec.product_id = rec.env['product.product'].search([('product_expense_type','=','advance')], limit=1)


