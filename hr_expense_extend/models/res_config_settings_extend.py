# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    financial_manager_id = fields.Many2one(comodel_name='hr.employee', string='Responsable Financiero',
                                           related='company_id.financial_manager_id',
                                           default_model="res.company",
                                           readonly=False)
    job_title_financial_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                     related='financial_manager_id.job_id')
    account_manager_id = fields.Many2one(comodel_name='hr.employee', string='Responsable Contable',
                                         related='company_id.account_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    job_title_account_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                   related='account_manager_id.job_id')
    general_manager_id = fields.Many2one(comodel_name='hr.employee', string='Aprobador',
                                         related='company_id.general_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    job_title_general_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                   related='general_manager_id.job_id')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Diario por defecto',
                                 related='company_id.journal_id',
                                 default_model="res.company",
                                 readonly=False)
    expense_manager_id = fields.Many2one(comodel_name='hr.employee', string='Aprobador de Gastos',
                                         related='company_id.expense_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    account_default_id = fields.Many2one(comodel_name='account.account', string='Cuenta de gasto',
                                         related='company_id.account_default_id',
                                         default_model="res.company",
                                         readonly=False)








