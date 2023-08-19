# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import json

class Applicant(models.Model):
    _inherit = "hr.applicant"
    _description = "Applicant"

    hr_requisition_domain = fields.Char(string='Requisition domain', compute='_domain_employee_id')
    hr_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition',
                                        string='Requisición de personal')

    @api.onchange('job_id')
    def _compute_select_hr_requisition_id(self):
        self.hr_requisition_id = self.job_id.hr_recruitment_requisition_id

    # function domain dynamic
    @api.depends('job_id')
    def _domain_employee_id(self):
        for rec in self:
            if rec.job_id:
                rec.hr_requisition_domain = json.dumps([('id', 'in', rec.job_id.hr_recruitment_requisition_ids.recruitment_requisition_id.ids),('state','=','approved')])
            else:
                rec.hr_requisition_domain = json.dumps([()])

