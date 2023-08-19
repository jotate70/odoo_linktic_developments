# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeePrivate(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'hr.employee.base', 'mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    _description = "Employee"

    # Campos nuevos en el modelo
    job_title_2 = fields.Many2one(comodel_name='hr.job', string="Job Title", store=True, required=True)