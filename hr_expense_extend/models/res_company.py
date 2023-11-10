from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    financial_manager = fields.Many2one(comodel_name='hr.employee', string='Gerente Financiero')
    general_manager = fields.Many2one(comodel_name='hr.employee', string='Aprobador')

