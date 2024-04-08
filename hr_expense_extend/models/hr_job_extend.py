# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Job(models.Model):
    _inherit = 'hr.job'

    job_type = fields.Selection([('president', 'Presidente'),
                                 ('vice_president', 'Vicepresidente'),
                                 ('director', 'Director'),
                                 ('department_manager', 'Gerente Procesos'),
                                 ('project_manager', 'Gerente Proyectos'),
                                 ('operational_staff', 'Personal Operativo')],
                                string='Tipo puesto de trabajo', store=True, default='operational_staff')





