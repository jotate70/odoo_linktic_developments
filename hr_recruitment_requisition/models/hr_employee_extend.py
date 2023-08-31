# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeePrivate(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'hr.employee.base', 'mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']
    _description = "Employee"

    # Campos nuevos en el modelo
    job_title_2 = fields.Many2one(comodel_name='hr.job', string="Job Title", store=True, required=True)
    rrhh_ticket_ids = fields.One2many(comodel_name='hr_recruitment_requisition',
                                      inverse_name='employee_id2',
                                      string="RRHH ticket", tracking=True)
    count_rrhh_ticket = fields.Integer(string='RRHH ticket count', compute='_compute_count_rrhh_ticket')

    # RRHH Ticket count
    def _compute_count_rrhh_ticket(self):
        for rec in self:
            rec.count_rrhh_ticket = len(rec.rrhh_ticket_ids)