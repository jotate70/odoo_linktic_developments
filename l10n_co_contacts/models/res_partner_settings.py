# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_vat = fields.Boolean(string='Numero de identificación')
    check_phone = fields.Boolean(string='Teléfono')
    check_mobile = fields.Boolean(string='Móvil')
    check_email = fields.Boolean(string='Correo electrónico')
    check_website = fields.Boolean(string='Sitio web')

    # Permite guardar valor en modelo transitorio
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.check_vat', self.check_vat)
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.check_phone', self.check_phone)
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.check_mobile', self.check_mobile)
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.check_email', self.check_email)
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.check_website', self.check_website)
        return res

    # permite obtener valores en modelo transitorio
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        partner_parameter_check_vat = ICPSudo.get_param('l10n_co_contacts_constraint.check_vat')
        partner_parameter_check_phone = ICPSudo.get_param('l10n_co_contacts_constraint.check_phone')
        partner_parameter_check_mobile = ICPSudo.get_param('l10n_co_contacts_constraint.check_mobile')
        partner_parameter_check_email = ICPSudo.get_param('l10n_co_contacts_constraint.check_email')
        partner_parameter_check_website = ICPSudo.get_param('l10n_co_contacts_constraint.check_website')

        res.update(
            check_vat=partner_parameter_check_vat,
            check_phone=partner_parameter_check_phone,
            check_mobile=partner_parameter_check_mobile,
            check_email=partner_parameter_check_email,
            check_website=partner_parameter_check_website,
        )
        return res







