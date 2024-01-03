from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    approved_vice_president_id = fields.Many2one(comodel_name='hr.employee', string='Approved vice-president')
    approved_advisor_id = fields.Many2one(comodel_name='hr.employee', string='Approved advisor')
