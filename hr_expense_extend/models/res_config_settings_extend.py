# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    financial_manager = fields.Many2one(comodel_name='hr.employee', string='Gerente Financiero',
                                        related='company_id.financial_manager',
                                        default_model="res.company",
                                        readonly=False,
                                        )
    job_title_financial_manager = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                  related='financial_manager.job_id')
    general_manager = fields.Many2one(comodel_name='hr.employee', string='Aprobador',
                                      related='company_id.general_manager',
                                      default_model="res.company",
                                      readonly=False,
                                      )
    job_title_general_manager = fields.Many2one(comodel_name='hr.job', string='Puesto de trabajo',
                                                related='general_manager.job_id')







