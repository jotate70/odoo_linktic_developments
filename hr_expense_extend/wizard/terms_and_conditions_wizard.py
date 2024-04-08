# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TermsConditionsWizard(models.TransientModel):
    _name = 'terms_conditions_transition_wizard'
    _description = "Terms and conditions wizard"

    travel_request_id = fields.Many2one(comodel_name='travel.request', string='Travel Request')
    message_text = fields.Text(string='Terminos y Condiciones')

    def do_action(self):
        for rec in self.travel_request_id:
            rec.action_confirm()
