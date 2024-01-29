# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Hrplatform(models.Model):
    _name = "hr_frequent_flyer_program"
    _description = "Frequent flyer program"

    name = fields.Char(string='Programa de viajero frecuente', required=True)
    code = fields.Char(string='Código', required=True)

    # SQL constraints
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El programa de viajero frecuente ya existe'),
    ]






