from odoo import fields, models

class L10nLatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    code = fields.Char(string='Code', store=True, size=2)

class Bank(models.Model):
    _inherit = 'res.bank'

    bank_code = fields.Char(string='Bank Code', store=True, size=4)

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_bank_account_id = fields.Many2one(comodel_name='res_partner_type_bank', string='Type bank account')

class ResPartnerTypeBank(models.Model):
    _name = 'res_partner_type_bank'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', size=2)





