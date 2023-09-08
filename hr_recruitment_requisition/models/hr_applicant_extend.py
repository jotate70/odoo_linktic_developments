# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import json


class Applicant(models.Model):
    _inherit = "hr.applicant"
    _description = "Applicant"

    name = fields.Char(string="Subject / Application Name", required=False,
                       help="Email subject for applications sent via email")
    partner_name = fields.Char(string="Applicant's Name", required=True)
    stage_domain = fields.Char(string='Stage Domain', compute='_compute_stage_domain')
    stage_id = fields.Many2one(comodel_name='hr.recruitment.stage', string='Stage', ondelete='restrict', tracking=True,
                               compute='_compute_stage', store=True, readonly=False,
                               domain='stage_domain',
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
    stage_type = fields.Selection([('new', 'New'),
                                   ('in_progress', 'In progress'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='stage_id.stage_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    hr_applicant_stage_log_ids = fields.One2many(comodel_name='hr_applicant_stage_log', inverse_name='hr_applicant_id',
                                                 string='Stage Logs',
                                                 copy=False)
    hired_stage = fields.Boolean(string='Hired Stage', related='stage_id.hired_stage',
                                 help="If checked, this stage is used to determine the hire date of an applicant")
    stage_after = fields.Many2one(comodel_name="hr.recruitment.stage", string="Stage After")
    state_level = fields.Integer(string='state count')
    hr_requisition_domain = fields.Char(string='Requisition domain', compute='_domain_employee_id')
    # hr_requisition_domain = fields.Char(string='Requisition domain')
    hr_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition',
                                        string='RRHH ticket')
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, related='stage_id.requires_approval')
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By',
                                 help='Immediate boss responsible for its approval.')
    manager_id2 = fields.Many2one(comodel_name='hr.employee', string='Alternative Approval',
                                  help='When the immediate boss is absent, the next person in charge must approve.')
    manager_before = fields.Many2one(comodel_name='hr.employee', string='Approval')
    manager_after_id = fields.Many2one(comodel_name='hr.employee', string='Manager next stage',
                                       help='Jefe inmediato respondable de su aprobación')
    requires_budget_approval = fields.Boolean(string='Requires budget approval',
                                              related='stage_id.requires_budget_approval')
    budget_amount = fields.Monetary(string='Budget amount', help='maximum amount you can approve.',
                                    related='stage_id.budget_amount')
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
    recruitment_type_id = fields.Many2many(comodel_name='hr_recruitment_type', relation='x_hr_recruitment_stage',
                                           column1='recruitment_stage_id', column2='recruitment_type_id',
                                           string='Recruitment Type', related='stage_id.recruitment_type_id',
                                           help='Match the stages with the types of personnel request.')

    # //////////////////////////////////////////////  Labor conditions  //////////////////////////////////////////////

    identification_type_id = fields.Many2one(comodel_name='l10n_latam.identification.type', string='ID Type', tracking=True)
    vat = fields.Char(string='No Document', tracking=True)
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type", tracking=True)
    negotiated_salary = fields.Monetary(string='Negotiated salary', tracking=True,
                                        help='Salary negotiated and agreed by the company and the candidate.')
    date_start = fields.Date(string='Start Date', tracking=True,
                             help="Start date of the contract (if it's a fixed-term contract).")
    contract_duration_qty = fields.Integer(string='Duration', tracking=True)
    contract_duration_sel = fields.Selection(selection=[('weekly', 'Weekly'),
                                                        ('month', 'Month'),
                                                        ('annual', 'Annual'),
                                                        ('undefined', 'Undefined')],
                                             string="To", default='month', tracking=True)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Account Analytic',
                                          check_company=True, tracking=True)
    required_mail = fields.Selection([('yes', 'Yes'),
                                         ('no', 'No'),],
                                        string='Required Mail', default='yes')
    mail_domain = fields.Char(string='Mail domain')
    computer_equipment = fields.Selection([('yes', 'Yes'),
                                         ('no', 'No'),],
                                        string='Computer Equipment', default='yes', tracking=True)
    os = fields.Selection([('windows', 'Windows'),
                           ('macos', 'MacOS'),
                           ('linux', 'Linux')],
                          string='OS', default='windows', tracking=True)
    tools = fields.Char(string='Tools', tracking=True)
    supervisor = fields.Many2one(comodel_name='hr.employee', string='Supervisor', tracking=True)
    contractor_company = fields.Many2one(comodel_name='res.partner', string='Contractor company', tracking=True)
    prepaid = fields.Text(string='Prepaid', tracking=True)

    # //////////////////////////////////////////////////  Funtions  //////////////////////////////////////////////////


    # Permite concatenar el name y la tipo solicitud
    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.hr_requisition_id.name) + ' - ' + str(rec.job_id.name) + ' - ' + str(rec.partner_name)
            result.append((rec.id, name))
        return result

    # function domain dynamic
    @api.depends('job_id')
    def _domain_employee_id(self):
        for rec in self:
            if rec.job_id:
                rec.hr_requisition_domain = json.dumps(
                    [('id', 'in', rec.job_id.hr_recruitment_requisition_ids.recruitment_requisition_id.ids),
                     ('state_type', '=', ['confirm', 'in_progress', 'recruitment']), ('recruitment_type', '=', '0')])
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

    # function domain dynamic
    @api.depends('recruitment_type_id')
    def _compute_stage_domain(self):
        for rec in self:
            if rec.recruitment_type_id:
                rec.stage_domain = json.dumps([('id', 'in', rec.recruitment_type_id.stage_id.ids)])
            else:
                rec.stage_domain = json.dumps([()])

    @api.onchange('display_name')
    def _compute_display_name_to_name(self):
        self.name = self.display_name

    # Select job RRHH Ticket
    @api.onchange('hr_requisition_id')
    def _compute_select_job_id(self):
        for rec in self.hr_requisition_id.recruitment_requisition_line:
            self.write({
                'job_id': rec.job_positions.id,
            })

    # data inicial
    @api.onchange('hr_requisition_id')
    def _compute_select_manager_id(self):
        vat = self.stage_id.sequence + 1
        self.state_level = self.stage_id.sequence
        self.stage_after = self.env['hr.recruitment.stage'].search([('sequence', '=', vat)], limit=1)

    def _compute_stage_after(self):
        vat = self.stage_after.sequence + 1
        self.state_level = vat
        self.stage_after = self.env['hr.recruitment.stage'].search([('sequence', '=', vat)], limit=1)
        if self.manager_after_id:
            self.manager_id = self.manager_after_id
            self.manager_before = self.manager_after_id
        else:
            self.manager_id = self.stage_id.manager_id
            self.manager_before = self.stage_id.manager_id
        self.uncapped_manager_id = self.stage_id.uncapped_manager_id
        if self.time_off == 'Ausente':
            self.manager_id2 = self.stage_id.optional_manager_id
            self.manager_before = self.stage_id.optional_manager_id
            self.uncapped_manager_id = self.stage_id.uncapped_manager_id
        elif self.time_off == 'Disponible':
            self.manager_id2 = self.stage_id.optional_manager_id
            self.manager_before = self.stage_id.manager_id
            self.uncapped_manager_id = self.stage_id.uncapped_manager_id

    def button_action_on_aprobation(self):
        if self.stage_after.requires_approval == 'yes' and self.requires_budget_approval == False:
            if self.manager_after_id:
                user = self.manager_after_id.user_id
            else:
                user = self.stage_after.manager_id.user_id
            note = 'Ha sido asignado para aprobar la aplicación de personal.'
            c = self.state_aprove + 1
            self.write({'state_aprove': c})
            # Código que crea una nueva actividad
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Aplicación de personal',
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
            c = self.state_aprove + 1
            self.write({'state_aprove': c})
        elif self.requires_budget_approval == True:
            if self.budget_amount < self.salary_expected:
                user = self.stage_after.uncapped_manager_id.user_id
            else:
                if self.manager_after_id:
                    user = self.manager_after_id.user_id
                else:
                    user = self.manager_before.user_id
            note = 'Ha sido asignado para validar negociación salarial del aplicante al cargo.'
            c = self.state_aprove + 1
            self.write({'state_aprove': c})
            # Código que crea una nueva actividad
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Aplicación de personal',
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
            c = self.state_aprove + 1
            self.write({'state_aprove': c})

    def compute_next_stage(self):
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')

        self.write({'stage_id': self.stage_after.id})
        self.button_action_on_aprobation()
        self._compute_stage_after()

    def open_stage_transition_wizard(self):
        if self.stage_id.requires_approval == 'yes' and self.requires_budget_approval == False:
            approved = self.manager_before
        elif self.requires_budget_approval == True:
            approved = self.uncapped_manager_id
        else:
            approved = self.user_id.employee_id
        new_wizard = self.env['hr_applicant_stage_transition_wizard'].create({
            'hr_applicant_id': self.id,
            'recruitment_type_id': self.recruitment_type_id.ids,
            'hr_recruitment_requisition_id': self.hr_requisition_id.id,
            'stage_id': self.stage_id.id,
            'requires_approval': self.stage_after.requires_approval,
            'manager_id': approved.id,
            'manager_after_id': self.stage_after.manager_id.id,
            'time_off': self.time_off,
            'time_off_related': self.time_off_related,
            'datetime_start': fields.datetime.now(),
        })
        return {
            'name': _('Stage Transition'),
            'view_mode': 'form',
            'res_model': 'hr_applicant_stage_transition_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def _action_after_approval(self):
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')
        self.write({'manager_id': self.stage_after.manager_id,
                    'manager_id2': self.stage_after.optional_manager_id})
        # Validación de disponibilidad de manager_id
        if self.time_off == 'Ausente':
            user = self.stage_after.optional_manager_id.user_id
            note = 'Ha sido asignado para aprobar la siguiente solicitud, El gerente responable se encuentra ausente'
            self.write({'manager_before': self.stage_after.optional_manager_id,
                        'uncapped_manager_id': self.stage_after.uncapped_manager_id})
        elif self.time_off == 'Disponible':
            user = self.stage_after.manager_id.user_id
            note = 'Ha sido asignado para aprobar la siguiente solicitud'
            self.write({'manager_before': self.stage_after.manager_id,
                        'uncapped_manager_id': self.stage_after.uncapped_manager_id})
        # Código que crea una nueva actividad
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {'activity_type_id': 4,
                       'summary': 'Solicitud de seleccion y contratacion de personal',
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

    def _action_requires_budget_approval(self):
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')
        # Código que crea una nueva actividad
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {'activity_type_id': 4,
                       'summary': 'Aprobación de monto salarial',
                       'automated': True,
                       'note': 'Ha sido asignado para negociar el salario propuesto',
                       'date_deadline': fields.datetime.now(),
                       'res_model_id': model_id,
                       'res_id': self.id,
                       'user_id': self.uncapped_manager_id.user_id.id,
                       }
        new_activity = self.env['mail.activity'].create(create_vals)
        # Escribe el id de la actividad en un campo
        self.write({'activity_id': new_activity})
        c = self.state_aprove + 1
        self.write({'state_aprove': c})

    def action_button_draft(self):
        state_id = self.env['hr.recruitment.stage'].search(
            [('state_type', '=', 'new'), ('recruitment_type_id', 'in', self.stage_id.recruitment_type_id.ids)],
            order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'state_aprove': 0,
                    'state_level': 0,
                    'manager_id': False,
                    'manager_id2': False,
                    'manager_before': False,
                    'requires_budget_approval': False})
        # Responsables iniciales
        self._compute_select_manager_id()
        self._compute_state_after()  # next stage check

    # Inherit
    @api.depends('job_id')
    def _compute_stage(self):
        for applicant in self:
            if applicant.job_id:
                if not applicant.stage_id:
                    stage_ids = self.env['hr.recruitment.stage'].search([
                        '|',
                        ('job_ids', '=', False),
                        ('job_ids', '=', applicant.job_id.id),
                        ('fold', '=', False)
                    ], order='sequence asc', limit=1).ids
                    applicant.stage_id = stage_ids[0] if stage_ids else False
            else:
                applicant.stage_id = False

    # Inherit
    def reset_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage = dict()
        for job_id in self.mapped('job_id'):
            default_stage[job_id.id] = self.env['hr.recruitment.stage'].search(
                ['|',
                 ('job_ids', '=', False),
                 ('job_ids', '=', job_id.id),
                 ('fold', '=', False)
                 ], order='sequence asc', limit=1).id
        for applicant in self:
            applicant.write(
                {'stage_id': applicant.job_id.id and default_stage[applicant.job_id.id],
                 'refuse_reason_id': False})
            self._compute_select_manager_id()



