from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    min_salary = fields.Monetary(string="Minimum Salary Range", currency_field='currency_id', widget="monetary")
    max_salary = fields.Monetary(string="Maximum Salary Range", currency_field='currency_id', widget="monetary")
    avg_salary = fields.Monetary(string="Average Salary", currency_field='currency_id', widget="monetary",
                                 compute="get_avg_salary_range")
    min_non_salary = fields.Monetary(string="Minimum Salary Range", currency_field='currency_id', widget="monetary")
    max_non_salary = fields.Monetary(string="Maximum Salary Range", currency_field='currency_id', widget="monetary")
    avg_non_salary = fields.Monetary(string="Average Non Salary", currency_field='currency_id', widget="monetary",
                                     compute="get_avg_salary_range")
    avg_job_salary = fields.Monetary(string="Average Job Paid Amount", currency_field='currency_id', widget="monetary",
                                     compute="get_avg_salary_range")
    salary_scale_ids = fields.One2many('hr.job.salary.scale', 'job_id', 'Salary Scales', copy=False)

    def get_avg_salary_range(self):
        for job in self:
            job.avg_salary = (job.min_salary + job.max_salary)/2
            job.avg_non_salary = (job.min_non_salary + job.max_non_salary)/2
            job.avg_job_salary = job.avg_salary + job.avg_non_salary
