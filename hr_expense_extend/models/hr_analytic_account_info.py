# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HrAnalyticAccountInfo(models.Model):
    _name = "hr_analytic_account_info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Analytic account Info"

    expense_sheet_id = fields.Many2one(comodel_name='hr.expense.sheet')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company)
    travel_request_id = fields.Many2one(comodel_name='travel.request', string='Solcitud de viaje')
    product_id = fields.Many2one(comodel_name='product.product', string="Producto",
                                 domain=[('can_be_expensed', '=', True)], required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Empleado")
    supplier_id = fields.Many2one(comodel_name='res.partner', string='Proveedor')
    supplier_type = fields.Many2one(comodel_name='l10n_latam.identification.type',
                                    string='Tipo de documento',
                                    help='Tipo de documento')
    supplier_vat = fields.Char(string='Nº identificación', help='Número de Documento')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica', check_company=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Etiquetas analíticas',
                                        states={'post': [('readonly', True)], 'done': [('readonly', True)]},
                                        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    unit_amount = fields.Float(string="Precio Unitario", store=True,
                               copy=True,
                               states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                       'approved': [('readonly', False)], 'refused': [('readonly', False)]},
                               digits='Product Price')
    quantity = fields.Float(string='Cantidad', readonly=True, default=1)
    amount_total = fields.Monetary(string='Costo', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    mode = fields.Selection([('analytic_account', 'Cuenta Analítica'),
                             ('supplier', 'Proveedor'),
                             ('items', 'Items')], default="draft", string="Estado")



