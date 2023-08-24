# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import json

class Applicant(models.Model):
    _inherit = "hr.applicant"
    _description = "Applicant"

    hr_applicant_stage_log_ids = fields.One2many(comodel_name='hr_applicant_stage_log', inverse_name='hr_recruitment_requisition_id', string='Stage Logs',
                                           copy=False)
    hired_stage = fields.Boolean(string='Hired Stage', related='stage_id.hired_stage',
                                 help="If checked, this stage is used to determine the hire date of an applicant")
    state_after = fields.Many2one(comodel_name="hr.recruitment.stage", string="Stage After")
    state_level = fields.Integer(string='state count')
    hr_requisition_domain = fields.Char(string='Requisition domain', compute='_domain_employee_id')
    hr_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition',
                                        string='RRHH ticket')
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, related='stage_id.requires_approval')
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By', related='stage_id.manager_id',
                                 help='Immediate boss responsible for its approval.')
    manager_id2 = fields.Many2one(comodel_name='hr.employee', string='Alternative Approval',
                                  help='When the immediate boss is absent, the next person in charge must approve.')
    manager_before = fields.Many2one(comodel_name='hr.employee', string='Approval')
    requires_budget_approval = fields.Boolean(string='Requires budget approval', related='stage_id.requires_budget_approval')
    budget_amount = fields.Monetary(string='Budget amount', help='maximum amount you can approve.')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    uncapped_manager_id = fields.Many2one(comodel_name='hr.employee', string='Uncapped manager',
                                          help='responsible for the stage that does not have a limit on the amount to be approved.')
    activity_id = fields.Integer(string='Activity')
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    state_aprove = fields.Integer(string='approval level')
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions'),
                                         ('2', 'Labor dismissal'),
                                         ('3', 'Disciplinary Process')],
                                        string=r'Recruitment Type', default='0', index=True,
                                        related='hr_requisition_id.recruitment_type')

    def open_stage_transition_wizard(self):
        if self.manager_before == self.env.user.employee_id:
            new_wizard = self.env['hr_applicant_stage_transition_wizard'].create({
                'hr_applicant_ids': self.id,
                'hr_recruitment_requisition_id': self.hr_requisition_id.id,
                'stage_id': self.stage_id.id,
                'manager_id': self.manager_id.id,
                'manager_id2': self.manager_id2.id,
                'manager_before': self.manager_before.id,
                'time_off': self.time_off,
                'time_off_related': self.time_off_related,
                'datetime_start': fields.datetime.now(),
            })
            return {
                'name': _('Stage Transition'),
                'view_mode': 'form',
                'res_model': 'hr_recruitment_requisition_stage_transition_wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': new_wizard.id,
            }
        else:
            raise UserError('El gerente responsable debe aprobar la solicitud.')

    # next stage check
    def _compute_state_after(self):
        vat = self.stage_id.sequence + 1
        self.state_level = self.stage_id.sequence
        self.state_after = self.env['hr.recruitment.stage'].search([('sequence', '=', vat)], limit=1)

    def compute_next_stage(self):
        self._compute_state_after()
        self.write({'stage_id': self.state_after.id})
        self._compute_select_manager_id()

    def button_action_on_aprobation(self):
        if self.manager_before.user_id == self.env.user:
            if self.state_after.requires_approval == 'yes':
                #  Marca actividad como hecha de forma automatica
                new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                new_activity.action_feedback(feedback='Es Aprobado')
                self.write({'manager_id': self.state_after.manager_id,
                            'manager_id2': self.state_after.optional_manager_id})
                note = ''; summary = ''
                if self.recruitment_type == '0':
                    summary = 'Solicitud de seleccion y contratacion de personal'
                elif self.recruitment_type == '1':
                    summary = 'Solicitud modificacion de condiciones laborales'
                elif self.recruitment_type == '2':
                    summary = 'Solicitud de desvinculacion Laboral'
                elif self.recruitment_type == '3':
                    summary = 'Solicitud de proceso Disciplinario'
                # Validación de disponibilidad de manager_id
                if self.time_off == 'Ausente':
                    user = self.state_after.optional_manager_id.user_id
                    note = 'Ha sido asignado para aprobar la siguiente solicitud, El gerente responable se encuentra ausente'
                    self.write({'manager_before': self.state_after.optional_manager_id})
                elif self.time_off == 'Disponible':
                    user = self.state_after.manager_id.user_id
                    note = 'Ha sido asignado para aprobar la siguiente solicitud'
                    self.write({'manager_before': self.state_after.manager_id})
                # Código que crea una nueva actividad
                model_id = self.env['ir.model']._get(self._name).id
                create_vals = {'activity_type_id': 4,
                               'summary': summary,
                               'automated': True,
                               'note': note,
                               'date_deadline': fields.datetime.now(),
                               'res_model_id': model_id,
                               'res_id': self.id,
                                'user_id': user.id,
                               }
                new_activity = self.env['mail.activity'].create(create_vals)
                # Escribe el id de la actividad en un campo
                self.write({'activity_id': new_activity})
                # Contador
                c = self.state_aprove + 1
                self.write({'state_aprove': c,
                            'state': self.state_after})
                self._compute_state_after()  # next stage check
            else:
                self.write({'stage_id': self.state_after})
                #  Marca actividad como hecha de forma automatica
                new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                new_activity.action_feedback(feedback='Es Aprobado')
                self._compute_state_after()  # next stage check
                # Contador de niveles de aprobación
                c = self.state_aprove + 1
                self.write({'state_aprove': c})
        else:
            raise UserError('El gerente responsable debe aprobar la solicitud.')

    # function domain dynamic
    @api.depends('job_id')
    def _domain_employee_id(self):
        for rec in self:
            if rec.job_id:
                rec.hr_requisition_domain = json.dumps([('id', 'in', rec.job_id.hr_recruitment_requisition_ids.recruitment_requisition_id.ids),('state_type','=',['confirm','in_progress','recruitment']),('recruitment_type','=','0')])
            else:
                rec.hr_requisition_domain = json.dumps([()])

    # Indica si el jefe inmediato está o no está ausente
    @api.depends('time_off_related')
    def _compute_number_of_days(self):
        for rec in self:
            if rec.manager_id:
                if rec.time_off_related == False:
                    rec.time_off = 'Disponible'
                else:
                    rec.time_off = 'Ausente'
            else:
                rec.time_off = False

    # Seleciona los responsables- de aprobaión inicial y departamento
    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        if self.time_off == 'Ausente':
            self.manager_id2 = self.stage_id.optional_manager_id
            self.manager_before = self.stage_id.optional_manager_id
        elif self.time_off == 'Disponible':
            self.manager_id2 = self.stage_id.optional_manager_id
            self.manager_before = self.stage_id.manager_id



