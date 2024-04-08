from odoo import fields, models, api, _


class ReportTask(models.Model):
    _name = 'linktic.report.task'
    _description = 'Report Task'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=1)
    code = fields.Char(string='Code')
    task_group_id = fields.Many2one(comodel_name='linktic.report.task.group', string='Task Group')

    # _sql_constraints = [
    #     ('name_unique', 'unique(name)', _("The name must be unique")),
    #     ('code_unique', 'unique(code)', _("The code must be unique"))]

