from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    financial_manager_id = fields.Many2one(comodel_name='res.users', string='Responsable Financiero')
    general_manager_id = fields.Many2one(comodel_name='res.users', string='Aprobador')
    account_manager_id = fields.Many2one(comodel_name='res.users', string='Responsable Contable')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Diario por defecto')
    journal_travel_id = fields.Many2one(comodel_name='account.journal', string='Diario viaticos por defecto')
    expense_manager_id = fields.Many2one(comodel_name='res.users', string='Aprobador de Gastos')
    account_default_id = fields.Many2one(comodel_name='account.account', string='Cuenta de gasto')

