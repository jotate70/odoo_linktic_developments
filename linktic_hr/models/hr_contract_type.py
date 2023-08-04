from odoo import fields, _, models, api

class HRContractType(models.Model):
    _inherit = "hr.contract.type"

    contract_type_id = fields.Selection([
        ('contract_type_defined', 'Contract_type_defined'),
        ('temporary_type_contract', 'Apprenticeship_type_contract'),
        ('apprenticeship_type_contract', 'Apprenticeship_contract'),
        ], default='contract_type_defined', string='Contract type defined',
        help="Allows you to filter the types of contracts for labor certifications.")


