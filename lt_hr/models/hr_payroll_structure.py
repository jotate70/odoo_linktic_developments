from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=False,
        copy=False, default=lambda self: self.env['res.company']._company_default_get())
    is_liquidation = fields.Boolean(string="Is Liquidation", default=False)
