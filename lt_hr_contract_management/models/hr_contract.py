from odoo import fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    salary_type = fields.Selection(
        [('basic', 'Basic'), ('integral', 'Integral'),
         ('support_sustainability', 'Support Sustainability')], required=True, tracking=True)
    contract_extension_count = fields.Integer(compute='_compute_extension_count', string="Count Contract Extension")
    contract_management_ids = fields.One2many('contract.management', 'contract_id', string="Contract Management")

    def _compute_extension_count(self):
        for rec in self:
            rec.contract_extension_count = len(rec.contract_management_ids)

    def view_contract_extension(self):
        return {
            'name': _('Contract Extension'),
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_model': 'contract.management',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('id', 'in', self.contract_management_ids.ids)]
        }
