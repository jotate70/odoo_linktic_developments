from odoo import fields, _, models, api

class HRContractType(models.Model):
    _inherit = "hr.contract.type"

    contract_type_id = fields.Selection([
        ('undefined_contract_type', 'Contract type undefined'),
        ('temporary_type_contract', 'Temporary type contract'),
        ('apprenticeship_type_contract', 'Apprenticeship type contract'),
        ], default='undefined_contract_type', string='Contract type',
        help="Allows you to filter the types of contracts for labor certifications.")


