from odoo import fields, models, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    product_expense_type = fields.Selection([('accommodation', 'Hospedaje'),
                                             ('journey', 'Viaje'),
                                             ('advance', 'Anticipo'),
                                             ('others', 'Otros')],
                                            default='others', string="Tipo de item")











