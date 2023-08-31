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
    rrhh_tickets_ids = fields.Many2many(comodel_name='hr_recruitment_requisition', relation='x_hr_employee_rrhh_ticket_rel',
                                        column1='hr_employee_id', column2='rrhh_ticket_id', string='RRHH Ticktes',
                                         help='.')

    # RRHH Ticket count
    def _compute_count_rrhh_ticket(self):
        for rec in self:
            rec.count_rrhh_ticket = len(rec.rrhh_tickets_ids)

    # @api.onchange('job_id')
    # def _related_rrhh_ticket(self):
    #     for rec in self.applicant_id:
    #         rec.hr_requisition_id.related_rrhh_ticteck_to_employee()
