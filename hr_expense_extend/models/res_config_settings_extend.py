# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    financial_manager_id = fields.Many2one(comodel_name='res.users', string='Responsable Financiero',
                                           related='company_id.financial_manager_id',
                                           default_model="res.company",
                                           readonly=False)
    job_title_financial_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                     related='financial_manager_id.employee_id.job_id')
    account_manager_id = fields.Many2one(comodel_name='res.users', string='Responsable Contable',
                                         related='company_id.account_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    job_title_account_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                   related='account_manager_id.employee_id.job_id')
    general_manager_id = fields.Many2one(comodel_name='res.users', string='Aprobador',
                                         related='company_id.general_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    job_title_general_manager_id = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                   related='general_manager_id.employee_id.job_id')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Diario por defecto',
                                 related='company_id.journal_id',
                                 default_model="res.company",
                                 domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
                                 readonly=False)
    journal_travel_id = fields.Many2one(comodel_name='account.journal', string='Diario viaticos por defecto',
                                 related='company_id.journal_travel_id',
                                 default_model="res.company",
                                 domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
                                 readonly=False)
    expense_manager_id = fields.Many2one(comodel_name='res.users', string='Aprobador de Gastos',
                                         related='company_id.expense_manager_id',
                                         default_model="res.company",
                                         readonly=False)
    account_default_id = fields.Many2one(comodel_name='account.account', string='Cuenta de gasto',
                                         related='company_id.account_default_id',
                                         default_model="res.company",
                                         domain="[('company_id', '=', company_id)]",
                                         readonly=False)
    message_text = fields.Text(string='Terminos y Condiciones')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("hr_expense.message_text", self.message_text)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        res['message_text'] = get_param('hr_expense.message_text')
        return res








