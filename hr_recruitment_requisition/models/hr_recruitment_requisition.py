# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import json

class RecruitmentRequisition(models.Model):
    _name = 'hr_recruitment_requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Recruitment Requisition"
    _order = 'priority desc, id desc'
    _check_company_auto = True

    def _get_default_state_id(self):
        return self.env["hr_requisition_state"].search([], limit=1).id

    @api.model
    def _read_group_state_ids(self, state, domain, order):
        stage_ids = self.env["hr_requisition_state"].search([])
        return stage_ids

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    name = fields.Char(copy=False, default='New', readonly=True)
    request_name = fields.Char(string='Request Name')
    priority = fields.Selection(
        [('0', 'All'),
         ('1', 'Low priority'),
         ('2', 'High priority'),
         ('3', 'Urgent')], string='Priority', default='0', index=True)
    color = fields.Integer(string="Color Index", default=0)
    state_domain = fields.Char(string='State Domain', compute='_compute_state_domain')
    state = fields.Many2one(comodel_name="hr_requisition_state", string="Stage", group_expand="_read_group_state_ids",
                            default=_get_default_state_id, tracking=True, ondelete="restrict", index=True, copy=False, domain='state_domain')
    state_after = fields.Many2one(comodel_name="hr_requisition_state", string="Stage After")
    state_level = fields.Integer(string='state count')
    state_blanket_order = fields.Many2one(comodel_name="hr_requisition_state", compute='_set_state')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='requested by', required=True,
                                  default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one(comodel_name='hr.department',
                                    string='Department', store=True)
    state_aprove = fields.Integer(string='approval level')
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By',
                                 help='Jefe inmediato respondable de su aprobación')
    manager_before = fields.Many2one(comodel_name='hr.employee', string='Approval Before')
    ceo = fields.Selection([('yes', 'Si'), ('no', 'No')], string='CEO o Gerente general', store=True,
                           default='no', help="Indica si el jefe principal de compañia, necesario para aprobaciones")
    manager_id2 = fields.Many2one(comodel_name='hr.employee', string='Alternative Approval',
                                      help='Cuando el jefe inmediato se encuentra ausente, debe aprobar el siguiente respondable')
    activity_id = fields.Integer(string='Activity')
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    estimated_date_admission = fields.Date(string='Entry date estimated', readonly=False, select=True, required=True)
    recruitment_type_id = fields.Many2one(comodel_name='hr_recruitment_type', string='Recruitment Type', required=True)
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions')],
                                        string=r'Recruitment Type', default='0', index=True,
                                        related='recruitment_type_id.recruitment_type')
    recruitment_requisition_line = fields.One2many(comodel_name='hr_recruitment_requisition_line',
                                                   inverse_name='recruitment_requisition_id',
                                                   string='Recruitment requisition line')
    recruitment_requisition_line_2 = fields.One2many(comodel_name='hr_recruitment_requisition_line',
                                                   inverse_name='recruitment_requisition_id',
                                                   string='Recruitment requisition line')
    recruitment_requisition_line_3 = fields.One2many(comodel_name='hr_recruitment_requisition_line',
                                                     inverse_name='recruitment_requisition_id',
                                                     string='Recruitment requisition line')
    hr_applicant_ids = fields.One2many(comodel_name='hr.applicant',
                                       inverse_name='hr_requisition_id',
                                       string='Aplicaciones')
    count_applicant = fields.Integer(string='Aplicaciones', compute='_compute_count_applicant')
    requisition_type = fields.Selection([('single_requisition', 'Single Requisition'),
                                         ('multiple_requisition', 'Multiple Requisition')],
                                        string=r'Requisition Type',
                                        related='recruitment_type_id.requisition_type')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    state_type = fields.Selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('in_progress', 'In Progress'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='state.state_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    ticket_stage_log_ids = fields.One2many(comodel_name='hr_recruitment_stage_log', inverse_name='hr_recruitment_requisition_id', string='Stage Logs',
                                           copy=False)
    assigned_id = fields.Many2one(comodel_name='res.users', string='Assigned', store=True, readonly=False, tracking=True,
                                  domain=lambda self: [('groups_id', 'in', self.env.ref('hr_recruitment.group_hr_recruitment_user').id)])
    activity_assigned_id = fields.Integer(string='Assigned activity')
    # Recruitment fields
    budget_post_id = fields.Many2one(comodel_name='account.budget.post', string='Budgetary Position',
                                     domain="[('is_payroll_position', '=', True)]")
    budget_value = fields.Float(string='Budget Value')
    # contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type")
    # contract_duration_qty = fields.Char(string='Contract qty')
    # contract_duration_sel = fields.Selection(selection=[('weekly', 'Weekly'),
    #                                                     ('month', 'Month'),
    #                                                     ('annual', 'Annual')],
    #                                           string="Contract Duration", default='month', tracking=True)
    # working_modality = fields.Selection(selection=[('mixed', 'Mixed'),
    #                                                ('in_person', 'In Person'),
    #                                                ('remote', 'Remote')],
    #                                     string="Working Modality", tracking=True, copy=False)
    # working_time = fields.Selection(selection=[('half', 'Half Time'),
    #                                            ('full', 'Full Time'),
    #                                            ('deliverables', 'Defined by deliverables')],
    #                                 string="Working Time", tracking=True, copy=False)
    profile_attachments_ids = fields.One2many(comodel_name='ir.attachment', inverse_name='hr_recruitment_requisition_id',
                                           string="Profile Attachments", tracking=True)
    count_attachments = fields.Integer(string='Aplicaciones', compute='_compute_count_attachments')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Account Analytic',
                                          check_company=True)
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, related='state.requires_approval')

    # function domain dynamic
    @api.depends('recruitment_type_id')
    def _compute_state_domain(self):
        for rec in self:
            if rec.recruitment_type_id:
                rec.state_domain = json.dumps([('id', 'in', rec.recruitment_type_id.state_id.ids)])
            else:
                rec.state_domain = json.dumps([()])

    #  recruitment type reset to recruitment_requisition_line
    @api.onchange('recruitment_type_id')
    def _compute_reset_recruitment_requisition_line(self):
        if self.recruitment_type_id:
            self.recruitment_requisition_line = False
            self.recruitment_requisition_line_2 = False
            self.recruitment_requisition_line_3 = False

    # Establece la requisición en estado cerrado
    def _compute_select_state_done(self):
        c = 0
        for rec in self.recruitment_requisition_line:
            if rec.recruited == 'not_recruited':
                c += 1
        if c == 0:
            self.write({'state': 'done'})
        else:
            return

    # Applicant count
    def _compute_count_applicant(self):
        for rec in self:
            rec.count_applicant = len(rec.hr_applicant_ids)

    # Attachments count
    def _compute_count_attachments(self):
        for rec in self:
            rec.count_attachments = len(rec.profile_attachments_ids)

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.depends('state')
    def _set_state(self):
        for requisition in self:
            requisition.state_blanket_order = requisition.state

    # Herencia del modelo crete para crear secuencias
    @api.model
    def create(self, vals):
        # Codigo adicional
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.ifpv') or 'New'
        result = super(RecruitmentRequisition, self).create(vals)
        return result

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

    # validación limite reclutamiento
    @api.onchange('recruitment_requisition_line')
    def _compute_constrains_recruitment_requisition_line(self):
        c = 0
        if self.requisition_type == 'single_requisition':
            if self.recruitment_requisition_line:
                for rec in self.recruitment_requisition_line:
                    c = c + 1
                    if c > 1:
                        raise UserError('El tipo de requisición permite una unica orden de recutlamiento')

    # validación limite reclutamiento
    @api.onchange('recruitment_requisition_line_2')
    def _compute_constrains_recruitment_requisition_line_2(self):
        c = 0
        if self.requisition_type == 'single_requisition':
            if self.recruitment_requisition_line_2:
                for rec in self.recruitment_requisition_line_2:
                    c = c + 1
                    if c > 1:
                        raise UserError('El tipo de requisición permite una unica orden de reclutamiento')

    # Seleciona los responsables- de aprobaión inicial y departamento
    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        self._compute_state_after()
        if self.employee_id and self.state_type == 'draft':
            self.manager_id = self.state_after.manager_id
            self.manager_id2 = self.state_after.optional_manager_id
            self.department_id = self.employee_id.department_id

    # next stage check
    def _compute_state_after(self):
        vat = self.state.sequence + 1
        self.state_level = self.state.sequence
        self.state_after = self.env['hr_requisition_state'].search([('sequence', '=', vat)], limit=1)

    # Action confirm
    def button_action_confirm(self):
        if self.recruitment_requisition_line:
            if self.state_type == 'draft':
                # mapping of stages created
                state_id = self.env['hr_requisition_state'].search([('state_type','=','confirm')], order="id asc", limit=1)
                self.write({'state': state_id.id})
                self.manager_id = self.state.manager_id
                self.manager_id2 = self.state.optional_manager_id
                note = ''; summary=''
                if self.recruitment_type == '0':
                    summary = 'Solicitud de seleccion y contratacion de personal'
                elif self.recruitment_type == '1':
                    summary = 'Solicitud modificacion de condiciones laborales'
                # Validación de disponibilidad de manager_id
                if self.time_off == 'Ausente':
                    self.manager_before = self.state.optional_manager_id
                    user = self.state.optional_manager_id.user_id
                    note = 'Ha sido asignado para verificar la información de la solicitud, y reasignar a un recurso de RRHH. '\
                           'El gerente responable se encuentra ausente.'
                elif self.time_off == 'Disponible':
                    self.manager_before = self.state.manager_id
                    user = self.state.manager_id.user_id
                    note = 'Ha sido asignado para verificar la información de la solicitud, y reasignar a un recurso de RRHH.'
                # Código que crea una nueva actividad
                model_id = self.env['ir.model']._get(self._name).id
                create_vals = {
                    'activity_type_id': 4,
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
                # Contador de niveles de aprobación
                c = self.state_aprove + 1
                self.write({'state_aprove': c})
                self._compute_state_after()  # next stage check
            else:
                raise UserError('Debe estar en estado borrador para poder confirmar.')
        else:
            raise UserError('No existe una linea de orden de reclutamiento')

    # Action on approbation
    def button_action_on_aprobation(self):
        if self.recruitment_requisition_line:
            if self.manager_before.user_id == self.env.user:
                self._action_state_assigned()
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
                    self.write({'state': self.state_after})
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Llama función actulizar cantidades a reclutar
                    for rec in self.recruitment_requisition_line:
                        rec.job_positions.update_no_of_recruitment(rec.no_of_recruitment)
                    self._compute_state_after()  # next stage check
                    # Contador de niveles de aprobación
                    c = self.state_aprove + 1
                    self.write({'state_aprove': c})
            else:
                raise UserError('El gerente responsable debe aprobar la solicitud.')
        else:
            raise UserError('No existe una linea de orden de reclutamiento')

    def button_action_done(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'done')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0'})

    def button_action_draft(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'draft')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0',
                    'state_aprove': 0,
                    'state_level': 0,
                    'activity_assigned_id': False,
                    'assigned_id': False,
                    'ticket_stage_log_ids': False,
                    'manager_before': False})
        # Responsables iniciales
        self._compute_select_manager_id()
        self._compute_state_after()  # next stage check

    def button_action_cancel(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'refused')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0'})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Is Refuse')
        new_activity2 = self.env['mail.activity'].search([('id', '=', self.activity_assigned_id)], limit=1)
        new_activity2.action_feedback(feedback='Is Refuse')
        # Llama función restablecer cantidades a reclutar
        if self.state_type == 'in_progress':
            for rec in self.recruitment_requisition_line:
                rec.job_positions.reset_no_of_recruitment(rec.no_of_recruitment)

    #   Función que crea actividad de usuario asigando para seguimiento de la solictud
    def _action_state_assigned(self):
        if self.activity_assigned_id == 0:
            if self.assigned_id:
                # note = ''; summary = ''
                if self.recruitment_type == '0':
                    summary = 'Seguimiento: selección y contratación de personal'
                    note = 'Ha sido asignado para realizar seguimiento a la solicitud de selección y contratación de personal.'
                elif self.recruitment_type == '1':
                    summary = 'Seguimiento: modificación de condiciones laborales'
                    note = 'Ha sido asignado para realizar seguimiento a la solicitud de modificación de condiciones laborales.'
                # Código que crea una nueva actividad
                model_id = self.env['ir.model']._get(self._name).id
                create_vals = {
                    'activity_type_id': 4,
                    'summary': summary,
                    'automated': True,
                    'note': note,
                    'date_deadline': fields.datetime.now(),
                    'res_model_id': model_id,
                    'res_id': self.id,
                    'user_id': self.assigned_id.id,
                }
                new_activity = self.env['mail.activity'].create(create_vals)
                # Escribe el id de la actividad en un campo
                self.write({'activity_assigned_id': new_activity})
            else:
                raise UserError(
                    'No se ha asignado una persona del área de RRHH para realizar seguimiento, por favor realizar asignación para continuar.')
        else:
            return

    # Función que cierra la requición
    def _compute_requisition_state_done(self):
        # mapping of stages created
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'done')],
                                                           order="id asc", limit=1)
        c = 0
        for rec in self.recruitment_requisition_line:
            if rec.recruited == 'not_recruited':
                c += 1
        if c == 0:
            self.write({'state': state_id})

    #   Wizard
    def open_stage_transition_wizard(self):
        new_wizard = self.env['hr_recruitment_requisition_stage_transition_wizard'].create({
            'helpdesk_ticket_id': self.id, 'stage_sequence': self.state_aprove,
            'valid_ticket_stage_ids': [(6, 0, self.recruitment_type_id.state_id.ids)]
        })
        return {
            'name': _('Stage Transition'),
            'view_mode': 'form',
            'res_model': 'hr_recruitment_requisition_stage_transition_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

class RecruitmentRequisitionLine(models.Model):
    _name = "hr_recruitment_requisition_line"
    _description = "Recruitment Requisition Line"

    sequence = fields.Integer(default=1)
    recruitment_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition', string='Recruitment Requisition')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    requisition_type = fields.Selection([('single_requisition', 'Single Requisition'),
                                         ('multiple_requisition', 'Multiple Requisition')],
                                        string=r'Requisition Type',
                                        related='recruitment_requisition_id.requisition_type')
    state = fields.Many2one(comodel_name="hr_requisition_state", string="Stage", related='recruitment_requisition_id.state')
    state_type = fields.Selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('in_progress', 'In Progress'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='state.state_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    recruitment_type = fields.Selection([('0', 'recruitment'), ('1', 'modifications of working conditions')],
                                        string=r'Recruitment Type', index=True,
                                        related='recruitment_requisition_id.recruitment_type')
    contract_addendum = fields.Selection([('signed', 'Signed'), ('not_signed', 'Not signed'), ],
                                         string='Contract Addendum', default='not_signed', index=True,
                                         compute='_compute_contract_addendum')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # ///////////////////////////////////////  recruitment  ////////////////////////////////////////////////////////

    job_positions_domain = fields.Char(string='Job Domain', compute='_domain_job_positions_domain')
    job_positions = fields.Many2one(comodel_name='hr.job', string="Job Positions", required=True)
    no_of_recruitment = fields.Integer(string='Amount', help='Number of new employees you expect to recruit.', default=1)
    estimated_date_admission = fields.Date(string='Entry date estimated', readonly=False, select=True)
    count_recruited = fields.Integer(string='Amount recruit', compute='_compute_count_recruited')
    recruited = fields.Selection([('recruited', 'Recruited'), ('not_recruited', 'Not Recruited'),],
                                 string='Recruited', default='not_recruited', index=True, compute='_compute_job_positions')
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type")
    contract_duration_qty = fields.Integer(string='Duration')
    contract_duration_sel = fields.Selection(selection=[('weekly', 'Weekly'),
                                                        ('month', 'Month'),
                                                        ('annual', 'Annual'),
                                                        ('undefined', 'Undefined')],
                                             string="To", default='month', tracking=True)
    working_modality = fields.Selection(selection=[('mixed', 'Mixed'),
                                                   ('in_person', 'In Person'),
                                                   ('remote', 'Remote')],
                                        string="Working Modality", tracking=True, copy=False)
    working_time = fields.Selection(selection=[('half', 'Half Time'),
                                               ('full', 'Full Time'),
                                               ('deliverables', 'Defined by deliverables')],
                                    string="Working Time", tracking=True, copy=False)
    observations = fields.Text(string='Observations')

    # ///////////////////////////////  modifications of working conditions  //////////////////////////////////////

    employee_domain = fields.Char(string='Employee Domain', compute='_domain_employee_id')
    # employee_domain = fields.Char(string='Employee Domain')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    contract_id = fields.Many2one(comodel_name='hr.contract', string='Current Contract')
    state_contract = fields.Selection([('draft', 'New'),
                                       ('open', 'Running'),
                                       ('close', 'Expired'),
                                       ('cancel', 'Cancelled')], string='Status Contract', tracking=True,
                                      help='Status of the contract')
    date_start = fields.Date(string='Start Date', tracking=True,
                             help="Start date of the contract (if it's a fixed-term contract).")
    date_end = fields.Date(string='End Date', tracking=True,
                           help="End date of the contract (if it's a fixed-term contract).")
    wage = fields.Float(string='Wage', tracking=True, help="Employee's monthly gross wage.")
    contract_welfare_aid = fields.Monetary(string='Welfare Assistance', related='contract_id.welfare_aid')
    contract_food_aid = fields.Monetary(string='Food Assistance', related='contract_id.food_aid')
    contract_transport_aid = fields.Monetary(string='Transport Assistance', related='contract_id.transport_aid')
    contract_bearing_aid = fields.Monetary(string='Bearing Assistance', related='contract_id.bearing_aid')
    contract_total_income = fields.Monetary(string='Total Income', related='contract_id.total_income')

    job_positions_after = fields.Many2one(comodel_name='hr.job', string="New job")
    updated_contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="New Contract Type")
    updated_contract_date_end = fields.Date(string='New Contract End Date')
    contract_wage_rise = fields.Monetary(string='Contract Wage Rise')
    updated_contract_total_income = fields.Monetary(string='New Total Income', compute='get_updated_contract_total_income')

    # Función creación para escribir secciones y notas
    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(job_positions=False)
        line = super(RecruitmentRequisitionLine, self).create(values)
        return line

    # Función escritura para escribir secciones y notas
    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                "You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type.")
        result = super(RecruitmentRequisitionLine, self).write(values)
        return result

    @api.depends('contract_wage_rise')
    def get_updated_contract_total_income(self):
        for ticket in self:
            if ticket.contract_wage_rise > 0:
                ticket.updated_contract_total_income = ticket.contract_wage_rise + ticket.contract_total_income
            else:
                ticket.updated_contract_total_income = False

    @api.onchange('job_positions')
    def _compute_employee_select(self):
        for rec in self:
            example = rec.env['hr.employee'].sudo().search([('active', '=', False), ('job_title', '=', rec.job_positions.ids)], limit=1, order='departure_date DESC')
            rec.write({'employee_id': example.id})

    @api.onchange('job_positions')
    def _compute_estimated_date_admission(self):
        for rec in self:
            rec.estimated_date_admission = rec.recruitment_requisition_id.estimated_date_admission

    #function domain dynamic
    @api.depends('job_positions')
    def _domain_job_positions_domain(self):
        a = []
        for rec in self:
            for rec2 in rec.env.user.employee_id.child_ids:
                a.append(rec2.job_id.id)
                for rec3 in rec2.child_ids:
                    a.append(rec3.job_id.id)
            jon_title = rec.env['hr.employee'].sudo().search(
                [('active', '=', True), ('active', '=', False), ('job_id', 'in', a)])
            employee = rec.env['hr.job'].sudo().search(
                [('id', 'in', jon_title.ids)])
            if employee:
                rec.job_positions_domain = json.dumps(['|',('id', 'in', employee.ids),
                                                       ('id','=',rec.env.user.employee_id.job_id.ids)])
            else:
                rec.job_positions_domain = json.dumps([])

    # function domain dynamic
    @api.onchange('job_positions')
    @api.depends('job_positions')
    def _domain_employee_id(self):
        for rec in self:
            employee = rec.env['hr.employee'].sudo().search([('job_id', 'in', rec.job_positions.ids), '|', ('active', '=', True), ('active', '=', False)])
            if employee:
                rec.employee_domain = json.dumps([('id', 'in', employee.ids), '|', ('active', '=', True), ('active', '=', False)])
            else:
                rec.employee_domain = json.dumps([()])

    # # function domain dynamic
    # @api.depends('employee_id')
    # def _domain_contract_id(self):
    #     for rec in self:
    #         employee = rec.env['hr.contract'].sudo().search([('job_id', 'in', rec.job_positions.ids), '|', ('active', '=', True), ('active', '=', False)])
    #         if employee:
    #             rec.employee_domain = json.dumps([('id', 'in', employee.ids), '|', ('active', '=', True), ('active', '=', False)])
    #         else:
    #             rec.employee_domain = json.dumps([()])

    @api.onchange('employee_id')
    def _compute_contract_wage(self):
        for rec in self:
            contract = rec.env['hr.contract'].sudo().search(
                [('employee_id', '=', rec.employee_id.ids), ('state', 'in', ['cancel', 'close', 'open'])], limit=1)
            rec.wage = contract.wage
            rec.contract_id = contract
            rec.contract_type_id = contract.contract_type_id
            rec.date_start = contract.date_start
            rec.date_end = contract.date_end
            rec.state_contract = contract.state

    def _compute_count_recruited(self):
        for rec in self:
            applicants = rec.env['hr.applicant'].search([('job_id','=',rec.job_positions.ids),
                                                          ('hr_requisition_id','=',rec.recruitment_requisition_id.ids),
                                                          ('stage_id.hired_stage','in',True)])
            if applicants:
                data = len(applicants.ids)
                rec.count_recruited = data
            else:
                rec.count_recruited = 0

    #Indica si se encuentra reclutado
    @api.depends('job_positions')
    def _compute_job_positions(self):
        for rec in self:
            if rec.no_of_recruitment == rec.count_recruited:
                rec.recruited = 'recruited'
                rec.recruitment_requisition_id._compute_requisition_state_done()
            else:
                rec.recruited = 'not_recruited'
                rec.recruitment_requisition_id._compute_requisition_state_done()

    # Indica si se encuentra reclutado
    @api.depends('job_positions')
    def _compute_contract_addendum(self):
        for rec in self:
            if rec.no_of_recruitment == rec.count_recruited:
                rec.contract_addendum = 'signed'
            else:
                rec.contract_addendum = 'not_signed'








