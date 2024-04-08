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
    # stage_id = fields.Many2one(comodel_name='hr.recruitment.stage', string='Stage', tracking=True,
    #                            compute='_compute_stage', store=True, readonly=False,
    #                            domain='stage_domain',
    #                            copy=False, index=True,
    #                            group_expand='_read_group_stage_ids')
    stage_id = fields.Many2one(comodel_name='hr.recruitment.stage', string='Stage', tracking=True,
                               compute='_compute_stage', store=True, readonly=False,
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
    stage_control = fields.Many2one(comodel_name='hr.recruitment.stage', string='Stage', index=True)
    stage_type = fields.Selection(selection=[('new', 'New'),
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
    signed_contract = fields.Boolean(string='Signed Contract', related='stage_id.signed_contract',
                                     help='Indicates whether the contract has actually been signed and the process has ended.')
    stage_after = fields.Many2one(comodel_name="hr.recruitment.stage", string="Stage After")
    state_level = fields.Integer(string='state count next')
    hr_requisition_domain = fields.Char(string='Requisition domain', compute='_domain_employee_id')
    # hr_requisition_domain = fields.Char(string='Requisition domain')
    hr_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition',
                                        string='RRHH ticket')
    requires_approval = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
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
    recruitment_type = fields.Selection(selection=[('0', 'recruitment'),
                                                   ('1', 'modifications of working conditions'),
                                                   ('2', 'Labor dismissal'),
                                                   ('3', 'Disciplinary Process')],
                                        string=r'Recruitment Type', default='0', index=True,
                                        related='hr_requisition_id.recruitment_type')
    recruitment_type_id = fields.Many2many(comodel_name='hr_recruitment_type', relation='x_hr_recruitment_stage',
                                           column1='recruitment_stage_id', column2='recruitment_type_id',
                                           string='Recruitment Type', related='stage_id.recruitment_type_id',
                                           help='Match the stages with the types of personnel request.')
    equipment_prioritization = fields.Selection(selection=[('high ', 'High'),
                                                           ('average', 'Avarage'),
                                                           ('low', 'Low'),
                                                           ('not_required', 'not required')],
                                                required=True, string='Computer equipment prioritization')

    # ////////////////////////////////////////////  Fields for contracts  ////////////////////////////////////////////

    reques_specifications = fields.Char(string='Request specifications', tracking=True)
    professional_card = fields.Char(string='Professional Card', tracking=True)
    expedition_date = fields.Date(string='Expedition Date', tracking=True)
    certifications = fields.Char(string='Certifications', tracking=True)
    academic_training = fields.Text(string='Academic Training', tracking=True)
    overall_experience = fields.Text(string='Overall Experience', tracking=True)
    specific_experience = fields.Text(string='Specific Experience', tracking=True)
    job_skills = fields.Text(string='Job Skills', tracking=True)

    # //////////////////////////////////////////////  Labor conditions  //////////////////////////////////////////////

    identification_type_id = fields.Many2one(comodel_name='l10n_latam.identification.type', string='ID Type', tracking=True)
    vat = fields.Char(string='No Document', tracking=True)
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type", tracking=True)
    negotiated_salary = fields.Monetary(string='Honorarium/Salary', tracking=True,
                                        help='Salary negotiated and agreed by the company and the candidate.')
    negotiated_food_bond = fields.Monetary(string='Food Bond', tracking=True,
                                           help='Food bond negotiated and agreed by the company and the candidate.')
    total_salary = fields.Monetary(string='Total salary', compute='_compoute_total_salary',
                                   help='Total Salary negotiated and agreed by the company and the candidate.')
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
    required_mail = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No'),],
                                        string='Required Mail', default='yes')
    mail_domain = fields.Char(string='Mail domain')
    computer_equipment = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No'),],
                                        string='Computer Equipment', default='yes', tracking=True)
    os = fields.Selection(selection=[('windows', 'Windows'),
                                     ('macos', 'MacOS'),
                                     ('linux', 'Linux')],
                          string='OS', default='windows', tracking=True)
    tools = fields.Char(string='Tools', tracking=True)
    supervisor = fields.Many2one(comodel_name='hr.employee', string='Supervisor', tracking=True)
    contractor_company = fields.Many2one(comodel_name='res.partner', string='Contractor company', tracking=True)
    prepaid = fields.Text(string='Prepaid', tracking=True)
    observations = fields.Html(string='observations', tracking=True)

    # //////////////////////////////////////////////////  Funtions  //////////////////////////////////////////////////

    def _related_prepaid_observations(self):
        self.observations = self.prepaid

    # Permite concatenar el name y la tipo solicitud
    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.hr_requisition_id.name) + ' - ' + str(rec.job_id.name) + ' - ' + str(rec.partner_name)
            result.append((rec.id, name))
        return result

    #  //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def control_stage_apply(self):
        self.write({'stage_id': self.stage_control.id})
        self._control_stage_recruitment()

    @api.onchange('stage_control')
    def _control_stage_recruitment(self):
        for rec in self:
            vat = []
            len1 = 0
            data = self.env['hr.recruitment.stage'].search([('recruitment_type_id', '=', self.recruitment_type_id.ids)])
            for rec2 in data:
                vat.append(rec2.id)
                len1 = len(vat)
            for i in range(0, len1-1):
                if vat[i] == rec.stage_control.id:
                    rec.stage_after = vat[i+1]
                    rec.state_level = i + 1
                    rec.state_aprove = i

    @api.onchange('display_name')
    def _compute_display_name_to_name(self):
        self.name = self.display_name

    # data inicial
    @api.onchange('hr_requisition_id')
    def _compute_select_manager_id(self):
        if self.hr_requisition_id:
            vat = self.stage_id.sequence + 2
            self.state_level = self.stage_id.sequence
            self.stage_after = self.env['hr.recruitment.stage'].search([('sequence', '=', vat)], limit=1)
            for rec in self.hr_requisition_id.recruitment_requisition_line:
                self.write({'job_id': rec.job_positions.id})

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    @api.depends()
    def _compoute_total_salary(self):
        self.total_salary = self.negotiated_salary + self.negotiated_food_bond

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

    # function domain dynamic
    @api.depends('job_id')
    def _domain_employee_id(self):
        for rec in self:
            if rec.job_id:
                rec.hr_requisition_domain = json.dumps(
                    [('id', 'in', rec.job_id.hr_recruitment_requisition_ids.recruitment_requisition_id.ids),
                     ('state_type', '=', ['confirm', 'in_progress', 'recruitment']),
                     ('recruitment_type', '=', '0')])
            else:
                rec.hr_requisition_domain = json.dumps([()])

    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def compute_stage_before(self):
        vat = self.stage_after.sequence - 1
        self.stage_after = self.env['hr.recruitment.stage'].search([('sequence', '=', vat)], limit=1)
        self.state_level = self.stage_after.sequence
        self.stage_id = self.env['hr.recruitment.stage'].search([('sequence', '=', vat-1)], limit=1)
        if self.time_off == 'Ausente':
            self.manager_id2 = self.stage_id.optional_manager_id
            self.manager_before = self.stage_id.optional_manager_id
            self.uncapped_manager_id = self.stage_id.uncapped_manager_id
        elif self.time_off == 'Disponible':
            self.manager_id2 = self.stage_id.manager_id
            self.manager_before = self.stage_id.manager_id
            self.uncapped_manager_id = self.stage_id.uncapped_manager_id

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
            self.manager_id2 = self.stage_id.manager_id
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
        if self.stage_after.stage_type == 'done':
            self.hr_requisition_id._compute_done_assigned()
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')

        self.write({'stage_id': self.stage_after.id})
        self.button_action_on_aprobation()
        self._compute_stage_after()

    def open_stage_transition_wizard(self):
        if self.stage_id.requires_approval == 'yes':
            if self.requires_budget_approval == False:
                approved = self.manager_id
            elif self.requires_budget_approval == True:
                approved = self.uncapped_manager_id
            # else:
            #     approved = self.user_id.employee_id
            if approved.user_id == self.env.user:
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
            else:
                raise UserError('No tiene permisos para aprobar la solicitud, solo el aprobador asignado puede confirmarla.')
        elif self.user_id == self.env.user:
            new_wizard = self.env['hr_applicant_stage_transition_wizard'].create({
                'hr_applicant_id': self.id,
                'recruitment_type_id': self.recruitment_type_id.ids,
                'hr_recruitment_requisition_id': self.hr_requisition_id.id,
                'stage_id': self.stage_id.id,
                'requires_approval': self.stage_after.requires_approval,
                'manager_id': self.user_id.employee_id.id,
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
        else:
            raise UserError('Sólo la persona asignada puede cambiar de etapa.')

    def archive_applicant(self):
        new_wizard = self.env['applicant.get.refuse.reason'].create({
            'hr_recruitment_requisition_id': self.hr_requisition_id.id,
            'stage_id': self.stage_id.id,
            'datetime_start': fields.datetime.now(),
            'applicant_ids': self.ids,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Refuse Reason'),
            'res_model': 'applicant.get.refuse.reason',
            'view_mode': 'form',
            'target': 'new',
            # 'context': {'default_applicant_ids': self.ids, 'active_test': False},
            'context': {'active_test': False},
            'res_id': new_wizard.id,
            'views': [[False, 'form']]
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



