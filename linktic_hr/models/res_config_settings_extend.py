# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hhrr_manager_id = fields.Many2one(comodel_name='hr.employee', string='HHRR Manager')
    hhrr_sign = fields.Binary(string='HHRR Sign')

    # Allows to save value in transient model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.hhrr_manager_id', self.hhrr_manager_id)
        self.env['ir.config_parameter'].set_param('l10n_co_contacts_constraint.hhrr_sign', self.hhrr_sign)
        return res

    # Allows to obtain values in transient model
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        hr_parameter_hhrr_manager_id = ICPSudo.get_param('l10n_co_contacts_constraint.hhrr_manager_id')
        hr_parameter_hhrr_sign = ICPSudo.get_param('l10n_co_contacts_constraint.hhrr_sign')

        res.update(
            check_vat=hr_parameter_hhrr_manager_id,
            check_phone=hr_parameter_hhrr_sign,
        )
        return res