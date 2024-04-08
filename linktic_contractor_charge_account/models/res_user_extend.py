from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_hours = fields.Integer(string='Allowed Hours')



