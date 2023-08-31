# -*- coding: utf-8 -*-
from odoo import api, fields, models

class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'

    # Discipline Categories
    code = fields.Char(string="Code", required=True, help="Category code")
    name = fields.Char(string="Name", required=True, help="Category name")
    category_type = fields.Selection([('disciplinary', 'Disciplinary Category'), ('action', 'Action Category')],
                                     string="Category Type", help="Choose the category type disciplinary or action")
    description = fields.Text(string="Details", help="Details for this category")