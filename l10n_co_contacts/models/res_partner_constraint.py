# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class l10n_co_contacts_constraint(models.Model):
    _inherit = 'res.partner'

    # campos relacionados de ajustes
    check_vat = fields.Boolean(string='Numero de identificación', compute='get_partner')
    check_phone = fields.Boolean(string='Teléfono', compute='get_partner')
    check_mobile = fields.Boolean(string='Móvil', compute='get_partner')
    check_email = fields.Boolean(string='Correo electrónico', compute='get_partner')
    check_website = fields.Boolean(string='Sitio web', compute='get_partner')

    # Función que llaman los valores en modelo settings
    def get_partner(self):
        self.check_vat = self.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_vat')
        self.check_phone = self.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_phone')
        self.check_mobile = self.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_mobile')
        self.check_email = self.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_email')
        self.check_website = self.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_website')
        return self.check_vat, self.check_phone, self.check_mobile, self.check_email, self.check_website




    
















