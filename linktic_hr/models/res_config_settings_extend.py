# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_manager_id = fields.Many2one(comodel_name='hr.employee', string='HHRR Manager',
                                    related='user_id.employee_id', readonly=False)
    enable_certificate_stamp = fields.Boolean(string='Enable Certificate Stamp')

    # Allows to save value in transient model
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('HrContract.hr_manager_id', self.hr_manager_id)
        self.env['ir.config_parameter'].set_param('HrContract.enable_certificate_stamp', self.enable_certificate_stamp)
        return res

    # Allows to obtain values in transient model
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        hr_parameter_hr_manager_id = ICPSudo.get_param('HrContract.hr_manager_id.ids')
        hr_parameter_enable_certificate_stamp = ICPSudo.get_param('HrContract.enable_certificate_stamp')

        res.update(
            hr_manager_id=hr_parameter_hr_manager_id,
            enable_certificate_stamp=hr_parameter_enable_certificate_stamp,
        )
        return res