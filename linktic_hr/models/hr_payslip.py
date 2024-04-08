from odoo import fields, _, models, api


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    def get_vigent_contracts(self):
        domain = [('company_id', '=', self.company_id.id), ('stage_employee', '=', 'active'), ('employee_type', 'in', ['employee', 'student', 'trainee'])]
        employees = self.sudo().env['hr.employee'].search(domain).filtered(lambda e: e.contract_id and e.contract_id.state == 'open')

        return employees.ids