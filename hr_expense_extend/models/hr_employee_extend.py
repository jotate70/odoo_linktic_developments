# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, Command

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    visa_country_id = fields.Many2one(comodel_name='res.country', string="País de la Visa")


