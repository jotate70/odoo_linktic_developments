# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class my_travel_request(models.Model):
    _name = "travel.mode"

    name = fields.Char('Travel Mode')