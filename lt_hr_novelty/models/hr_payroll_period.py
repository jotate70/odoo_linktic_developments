from odoo import fields, models


class HrPayrollPeriod(models.Model):
    _inherit = 'hr.payroll.period'

    novelty_date_start = fields.Date('Date start', required=True, tracking=True)
    novelty_date_end = fields.Date('Date end', required=True, tracking=True)
