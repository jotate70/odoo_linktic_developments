from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from odoo.osv import expression

class HrPayrollParameter(models.Model):
    _name = "hr.payroll.parameter"
    _description = "HR Parameter"

    name = fields.Char('Name')
    code = fields.Char('Code')
    company_ids = fields.Many2many('res.company', string="Companies")
    line_ids = fields.One2many('hr.payroll.parameter.line', 'parameter_id')


class HrPayrollParameterLine(models.Model):
    _name = "hr.payroll.parameter.line"
    _description = "HR Parameter Values"

    parameter_id = fields.Many2one('hr.payroll.parameter')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    no_smlv = fields.Integer('No. SMLV (if applies)')
    value = fields.Float('Value')

    @api.constrains('date_start', 'date_end')
    def _check_line_date(self):
        domains = [[('date_start', '<', line.date_end), ('date_end', '>=', line.date_start),
                    ('parameter_id', '=', line.parameter_id.id), ('id', '!=', line.id)] for line in
                   self.filtered('parameter_id')]
        domain = expression.OR(domains)

        if self.search_count(domain):
            raise ValidationError(_("There are multiple lines value in which the date range overlaps"))
