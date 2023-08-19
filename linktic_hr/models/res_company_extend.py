# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = "res.company"

    certificate_stamp = fields.Binary(string='Certificate stamp')
    hr_manager_id = fields.Many2one(comodel_name='hr.employee', string='HHRR Manager')
    certificate_template = fields.Binary(string='Certificate Template')