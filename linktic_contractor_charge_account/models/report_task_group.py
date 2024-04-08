from odoo import fields, models, api, _


class ReportTaskGroup(models.Model):
    _name = 'linktic.report.task.group'
    _description = 'Report Task'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    report_task_ids = fields.One2many(comodel_name='linktic.report.task', inverse_name='task_group_id',
                                      string='Report Task', readonly=False)

    _sql_constraints = [
        ('name_unique', 'unique(name)', _("The name must be unique")),
        ('code_unique', 'unique(code)', _("The code must be unique"))]

