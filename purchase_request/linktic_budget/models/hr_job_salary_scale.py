from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _name = 'hr.job.salary.scale'
    _description = "salary scales for jobs"

    job_id = fields.Many2one('hr.job', string="Job", required=True)
    name = fields.Char(string='Seniority')
    currency_id = fields.Many2one(string="Currency", related='job_id.company_id.currency_id', readonly=True)
    min_salary = fields.Monetary(string="Minimum Salary Range", currency_field='currency_id', widget="monetary",
                                 required=True)
    max_salary = fields.Monetary(string="Maximum Salary Range", currency_field='currency_id', widget="monetary",
                                 required=True)
    avg_salary = fields.Monetary(string="Average Salary", currency_field='currency_id', widget="monetary",
                                 compute="get_avg_salary_range")
    min_non_salary = fields.Monetary(string="Minimum Non Salary Range", currency_field='currency_id', widget="monetary",
                                     required=True)
    max_non_salary = fields.Monetary(string="Maximum Non Salary Range", currency_field='currency_id', widget="monetary",
                                     required=True)
    avg_non_salary = fields.Monetary(string="Average Non Salary", currency_field='currency_id', widget="monetary",
                                     compute="get_avg_salary_range")
    avg_job_salary = fields.Monetary(string="Average Job Paid Amount", currency_field='currency_id', widget="monetary",
                                     compute="get_avg_salary_range")

    @api.onchange('max_non_salary', 'max_salary')
    def validate_min_max_consistency(self):
        for record in self:
            if 0 < record.max_non_salary < record.min_non_salary:
                raise ValidationError(_("The max range of non salary cannot be lesser than min range"))
            if 0 < record.max_salary < record.min_salary:
                raise ValidationError(_("The max range of salary cannot be lesser than min range"))

    @api.onchange('max_non_salary', 'max_salary', 'min_non_salary', 'min_salary')
    def validate_non_negative_values(self):
        for record in self:
            if record.min_non_salary < 0 or record.max_non_salary < 0 or record.max_salary < 0 or record.min_salary < 0:
                raise ValidationError(_("Cannot put negative values on salary"))

    def get_avg_salary_range(self):
        for job in self:
            job.avg_salary = (job.min_salary + job.max_salary) / 2
            job.avg_non_salary = (job.min_non_salary + job.max_non_salary) / 2
            job.avg_job_salary = job.avg_salary + job.avg_non_salary
