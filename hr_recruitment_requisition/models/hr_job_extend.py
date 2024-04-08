# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Job(models.Model):
    _inherit = 'hr.job'
    _description = "Job Position"

    hr_recruitment_requisition_ids = fields.One2many(comodel_name='hr_recruitment_requisition_line', inverse_name='job_positions',
                                                     string='Recruitment Requisition Line')
    hr_recruitment_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition', string='Recruitment Requisition',
                                                    compute='_compute_recruitment_requisition_id')
    state_requisition = fields.Boolean(string='State Requisition', compute='_compute_state_requisition')

    # Valida si existe requisición asociada en curso
    @api.depends('hr_recruitment_requisition_ids')
    def _compute_state_requisition(self):
        for rec in self:
            c = 0
            for rec2 in rec.hr_recruitment_requisition_ids:
                if rec2.state_type in ['confirm','in_progress','recruitment']:
                    c = c + 1
            if c > 0:
                rec.state_requisition = True
            else:
                rec.state_requisition = False

    # Valida si existe requisición asociada en curso
    @api.depends('hr_recruitment_requisition_ids')
    def _compute_recruitment_requisition_id(self):
        data = self.env['hr_recruitment_requisition_line'].search([('id','in',self.hr_recruitment_requisition_ids.ids),('state_type','in',['in_progress','recruitment'])], limit=1)
        if data:
            self.hr_recruitment_requisition_id = data.recruitment_requisition_id
        else:
            self.hr_recruitment_requisition_id = False

    # Actualiza cantidad a reclutar (suma)
    def update_no_of_recruitment(self,vat):
        self.no_of_recruitment += vat

    # Actualiza cantidad a reclutar (resta)
    def reset_no_of_recruitment(self,vat):
        self.no_of_recruitment -= vat









