# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrExpensesType(models.Model):
    _name = "hr_type_travel_expenses"

    product_id = fields.Many2one(comodel_name='product.product', string="Item", domain=[('can_be_expensed', '=', True), ('product_expense_type','=','advance')], required=True)
    amount_president = fields.Monetary(string='Presidente')
    amount_vice_president = fields.Monetary(string='Vicepresidente')
    amount_director = fields.Monetary(string='Director')
    amount_department_manager = fields.Monetary(string='Gerente Procesos')
    amount_project_manager = fields.Monetary(string='Gerente Proyectos')
    amount_operational_staff = fields.Monetary(string='Personal Operativo')
    currency_id = fields.Many2one(comodel_name='res.currency', default=lambda self: self.env.company.currency_id)
