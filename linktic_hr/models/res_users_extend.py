# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = "res.users"

    hhrr_sign = fields.Binary(string='HHRR Sign')