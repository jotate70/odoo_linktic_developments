from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    is_policy_product = fields.Boolean('Is Policy', default=False)
