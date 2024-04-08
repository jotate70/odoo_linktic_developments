# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ContractType(models.Model):
    _inherit = 'hr.contract.type'

    budget_post_ids = fields.Many2many(comodel_name='account.budget.post',
                                       relation='budget_post_rel_contract_type',
                                       column1='budget_post_id',
                                       column2='contract_type_id',
                                       string="Budgetary Position",
                                       domain="[('is_payroll_position', '=', True)]")