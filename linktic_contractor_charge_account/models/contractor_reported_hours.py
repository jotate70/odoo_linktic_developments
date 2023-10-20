from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class ContractorReportedHours(models.Model):
    _name = "hr.contractor.reported.hours"
    _description = "Contractor Reported Hours"

    date = fields.Date(string="Date")
    employee_name = fields.Char(string="Employee Name")
    employee_identification = fields.Char(string='Employee Identification')
    hours = fields.Integer(string="Hours")
    account_analytic_code = fields.Char(string="Cost Center")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', store=True, compute="_get_employee_user")

    @api.depends('employee_identification')
    def _get_employee_user(self):
        for record in self:
            if record.employee_identification:
                employee_obj = self.env['hr.employee'].search(
                    [('identification_id', '=', record.employee_identification)])
                if employee_obj:
                    record.user_id = employee_obj.user_id
            else:
                record.user_id = False
