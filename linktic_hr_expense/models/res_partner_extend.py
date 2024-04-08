from odoo import fields, _, models, api, Command

class Partner(models.Model):
    _inherit = "res.partner"

    property_account_advance_id = fields.Many2one(comodel_name='account.account', string='Cuenta para anticipo',
                                                  domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]",
                                                  default=lambda self: self.env.company.property_account_advance_id)
    def _compure_related_property_account_advance_id(self):
        self.property_account_advance_id = self.env.company.property_account_advance_id




