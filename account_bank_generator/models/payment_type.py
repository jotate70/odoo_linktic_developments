from odoo import api, fields, models, _


class PaymentType(models.Model):
    _name = 'payment.type'
    _description = 'Payment Type'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code', size=2)
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')
    active = fields.Boolean(default=True)
    required_account_bank = fields.Boolean('Required account bank?', default=False)

    _sql_constraints = [
        ('name_unique', 'unique(name)', _("The name must be unique")),
        ('code_unique', 'unique(code, bank_id)', _("The code must be unique per bank"))]

#
