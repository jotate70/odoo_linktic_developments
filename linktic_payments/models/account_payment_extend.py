from odoo import _, api, Command, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_check = fields.Boolean(string='Payment Check', tracking=True)