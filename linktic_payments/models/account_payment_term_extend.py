from odoo import fields, _, models, api

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    term_type = fields.Selection(selection=[('credit_type', 'Credit Type'),
                                            ('others', 'Others')],
                                 default='others',
                                 required=True,
                                 string='Term Type')


