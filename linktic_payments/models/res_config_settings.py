from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    approved_vice_president_id = fields.Many2one(comodel_name='hr.employee', string='Approved vice-president',
                                                 help='Responsible for validating all bank payments',
                                                 related='company_id.approved_vice_president_id', readonly=False)
    approved_advisor_id = fields.Many2one(comodel_name='hr.employee', string='Approved advisor',
                                          help='Responsible for validating bank payments',
                                          related='company_id.approved_advisor_id', readonly=False)
