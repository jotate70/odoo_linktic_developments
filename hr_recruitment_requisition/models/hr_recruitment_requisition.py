# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
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

    # ///////////////////////////////////////////// General fields ////////////////////////////////////////////////

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    name = fields.Char(copy=False, default='New', readonly=True)
    request_name = fields.Char(string='Request Name')
    priority = fields.Selection(
        [('0', 'All'),
         ('1', 'Low priority'),
         ('2', 'High priority'),
         ('3', 'Urgent')], string='Priority', tracking=True, default='0', index=True)
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
    manager_after_id = fields.Many2one(comodel_name='hr.employee', string='Manager next stage',
                                       help='Jefe inmediato respondable de su aprobación desde ventana emergente')
    activity_id = fields.Integer(string='Activity')
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    estimated_date_admission = fields.Date(string='Entry date estimated', readonly=False, select=True)
    recruitment_type_id = fields.Many2one(comodel_name='hr_recruitment_type', string='Recruitment Type', required=True)
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions'),
                                         ('2', 'Labor dismissal'),
                                         ('3', 'Disciplinary Process')],
                                        string=r'Recruitment Type', default='0', index=True,
                                        related='recruitment_type_id.recruitment_type')
    recruitment_requisition_line = fields.One2many(comodel_name='hr_recruitment_requisition_line',
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
                                   ('recruitment', 'Recruitment'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='state.state_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    hr_recruitment_stage_log_ids = fields.One2many(comodel_name='hr_recruitment_stage_log', inverse_name='hr_recruitment_requisition_id', string='Stage Logs',
                                           copy=False)
    assigned_id = fields.Many2one(comodel_name='res.users', string='Assigned', store=True, readonly=False, tracking=True,
                                  domain=lambda self: [('groups_id', 'in', self.env.ref('hr_recruitment.group_hr_recruitment_user').id)])
    activity_assigned_id = fields.Integer(string='Assigned activity')
    # Recruitment fields
    budget_post_id = fields.Many2one(comodel_name='account.budget.post', string='Budgetary Position',
                                     domain="[('is_payroll_position', '=', True)]")
    budget_value = fields.Float(string='Budget Value')
    attachment_profile_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='x_profile_attachment_rel',
                                                         column1='recruitment_requisition_id', column2='attachment_id',
                                                         string="Attachments", help="Profile Attachments", tracking=True)
    profile_attachments_ids = fields.One2many(comodel_name='ir.attachment', inverse_name='hr_recruitment_requisition_id',
                                           string="Profile Attachments", tracking=True)
    count_attachments = fields.Integer(string='Aplicaciones', compute='_compute_count_attachments')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Account Analytic',
                                          check_company=True)
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval',
                                         help='Indicates if this stage requires approval in the personnel request.',
                                         store=True, related='state.requires_approval')
    description = fields.Html(string='Description', store=True, translate=True, sanitize_style=True)
    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='x_hr_employee_rrhh_ticket_rel',
                                   column1='rrhh_ticket_id', column2='hr_employee_id', string='Employee',
                                   help='')

    # ////////////////////////////////////  Modifications of working conditions  ///////////////////////////////////

    employee_domain = fields.Char(string='Domain Employee')
    employee_id2 = fields.Many2one(comodel_name='hr.employee', string='Employee')
    job_positions_domain = fields.Char(string='Job positions domain', compute='_domain_domain_job_positions_id')
    job_positions = fields.Many2one(comodel_name='hr.job', domain='job_positions_domain', string="Job Positions")
    contract_domain = fields.Char(string='Contract Domain', compute='_contract_domain')
    contract_id = fields.Many2one(comodel_name='hr.contract', domain='contract_domain', string='Current Contract')
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type",
                                       related='contract_id.contract_type_id')
    state_contract = fields.Selection([('draft', 'New'),
                                       ('open', 'Running'),
                                       ('close', 'Expired'),
                                       ('cancel', 'Cancelled')], string='Status Contract',
                                      help='Status of the contract', related='contract_id.state')
    date_start = fields.Date(string='Start Date', tracking=True, related='contract_id.date_start',
                             help="Start date of the contract (if it's a fixed-term contract).")
    date_end = fields.Date(string='End Date', tracking=True, related='contract_id.date_start',
                           help="End date of the contract (if it's a fixed-term contract).")
    company_id2 = fields.Many2one(comodel_name='res.company', string='Company', related='contract_id.company_id')
    department_id2 = fields.Many2one(comodel_name='hr.department', string='Department',
                                     related='contract_id.department_id')
    wage = fields.Monetary(string='Wage', help="Employee's monthly gross wage.", related='contract_id.wage')
    contract_welfare_aid = fields.Monetary(string='Welfare Assistance', related='contract_id.welfare_aid')
    contract_food_aid = fields.Monetary(string='Food Assistance', related='contract_id.food_aid')
    contract_transport_aid = fields.Monetary(string='Transport Assistance', related='contract_id.transport_aid')
    contract_bearing_aid = fields.Monetary(string='Bearing Assistance', related='contract_id.bearing_aid')
    contract_total_income = fields.Monetary(string='Total Income', related='contract_id.total_income')
    job_positions_after = fields.Many2one(comodel_name='hr.job', string="New job select",  tracking=True)
    job_positions_after_text = fields.Char(string='New job')
    company_id3 = fields.Many2one(comodel_name='res.company', string='Company',  tracking=True)
    department_id3 = fields.Many2one(comodel_name='hr.department', string='Department',  tracking=True)
    updated_contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="New Contract Type",  tracking=True)
    updated_contract_date_end = fields.Date(string='New Contract End Date',  tracking=True)
    contract_wage_rise = fields.Monetary(string='Contract Wage Rise',  tracking=True)
    updated_contract_total_income = fields.Monetary(string='New Total Income', compute='get_updated_contract_total_income')

    # ///////////////////////////////////////////// Labor dismissal /////////////////////////////////////////////////

    resignation_type = fields.Selection([('dismissal', 'Dismissal'),
                                       ('resignation', 'Resignation'),
                                       ('non-renewal', 'Non-renewal')], default='resignation', required=True,
                                        string='Resignation type', tracking=True)

    # ///////////////////////////////////////////// Disciplinary process //////////////////////////////////////////////////////

    discipline_reason = fields.Many2one(comodel_name='discipline.category', string='Reason', tracking=True,
                                        help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee", tracking=True,
                              help='Employee have to give Explanation to manager about the violation of discipline')
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string="Attachments",
                                      help="Employee can submit any documents which supports their explanation")

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # Validación de puesto de trabajo en reclutamiento
    def compute_constraints_job_id(self):
        if self.state_type == 'in_progress'and self.recruitment_type == '0':
            for rec in self.recruitment_requisition_line:
                if rec.job_positions:
                    return
                else:
                    raise UserError('Debes agregar un puesto de trabajo en la orden de reclutamiento para poder continuar.')

    # auto-select fields contract relation
    @api.onchange('employee_id2')
    def _compute_contract_wage(self):
        for rec in self:
            if rec.employee_id2:
                rec.employee_ids = rec.employee_id2 # Related employee
                rec.job_positions = rec.employee_id2.job_id
                rec.contract_id = rec.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id2.ids)], limit=1)

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

    # Seleciona los responsables de aprobaión inicial y departamento
    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        self._compute_state_after()
        if self.employee_id and self.state_type == 'draft':
            self.manager_id = self.state_after.manager_id
            self.manager_id2 = self.state_after.optional_manager_id
            self.department_id = self.employee_id.department_id

    #  recruitment type reset to recruitment_requisition_line
    @api.onchange('recruitment_type_id')
    def _compute_reset_recruitment_requisition_line(self):
        if self.recruitment_type_id:
            self.recruitment_requisition_line = False
            self.employee_id2 = False
            self.job_positions = False
            self.contract_id = False
            self.job_positions_after = False
            self.updated_contract_type_id = False
            self.company_id3 = False
            self.department_id3 = False
            self.updated_contract_date_end = False
            self.contract_wage_rise = False

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    # function domain dynamic job position
    @api.depends('employee_id2')
    def _domain_domain_job_positions_id(self):
        for rec in self:
            job = rec.env['hr.job'].sudo().search(
                [('employee_ids', 'in', rec.employee_id2.ids)], limit=1)
            if job:
                rec.job_positions_domain = json.dumps([('id', '=', job.ids)])
            else:
                rec.job_positions_domain = json.dumps([('id','=',False)])

    # function domain dynamic state
    @api.depends('recruitment_type_id')
    def _compute_state_domain(self):
        for rec in self:
            if rec.recruitment_type_id:
                rec.state_domain = json.dumps([('id', 'in', rec.recruitment_type_id.state_id.ids)])
            else:
                rec.state_domain = json.dumps([('id','=',False)])

    # function domain dynamic contract
    @api.depends('contract_id')
    def _contract_domain(self):
        for rec in self:
            contract = rec.env['hr.contract'].sudo().search(
                [('employee_id', '=', rec.employee_id2.ids)])
            if contract:
                rec.contract_domain = json.dumps([('id', 'in', contract.ids)])
            else:
                rec.contract_domain = json.dumps([('id','=',False)])

    # Permite concatenar el name y la tipo solicitud
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name + ' - ' + rec.recruitment_type_id.name
            result.append((rec.id, name))
        return result

    # Establece la requisición en estado cerrado
    def _compute_select_state_done(self):
        c = 0
        for rec in self.recruitment_requisition_line:
            if rec.recruited == 'not_recruited':
                c += 1
        if c == 0:
            state_id = self.env['hr_requisition_state'].search([('state_type','=','done'),('recruitment_type_id','in',self.recruitment_type_id.ids)],
                                                               order="id asc", limit=1)
            self.write({'state': state_id.id})
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

    # Compute wage rise
    @api.depends('contract_wage_rise')
    def get_updated_contract_total_income(self):
        for ticket in self:
            if ticket.contract_wage_rise > 0:
                ticket.updated_contract_total_income = ticket.contract_wage_rise + ticket.contract_total_income
            else:
                ticket.updated_contract_total_income = False

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

    # next stage check
    def _compute_state_after(self):
        vat = self.state.sequence + 1
        self.state_level = self.state.sequence
        self.state_after = self.env['hr_requisition_state'].search([('sequence', '=', vat)], limit=1)

    # Action confirm
    def button_action_confirm(self):
        if self.recruitment_requisition_line or self.recruitment_type != '0':
            if self.state_type == 'draft':
                # Select job in recruitment requisition line
                # mapping of stages created
                state_id = self.env['hr_requisition_state'].search([('state_type','=','confirm'),('recruitment_type_id','in',self.recruitment_type_id.ids)],order="id asc",limit=1)
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

    def button_action_done(self):
        state_id = self.env['hr_requisition_state'].search([('state_type','=','done'),('recruitment_type_id','in',self.recruitment_type_id.ids)],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0'})

    def button_action_draft(self):
        state_id = self.env['hr_requisition_state'].search([('state_type','=','draft'),('recruitment_type_id','in',self.recruitment_type_id.ids)],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0',
                    'state_aprove': 0,
                    'state_level': 0,
                    'activity_assigned_id': False,
                    'hr_recruitment_stage_log_ids': False,
                    'manager_before': False})
        # Responsables iniciales
        self._compute_select_manager_id()
        self._compute_state_after()  # next stage check

    def button_action_cancel(self):
        state_id = self.env['hr_requisition_state'].search([('state_type','=','refused'),('recruitment_type_id','in',self.recruitment_type_id.ids)],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0'})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Is Refuse')
        new_activity2 = self.env['mail.activity'].search([('id', '=', self.activity_assigned_id)], limit=1)
        new_activity2.action_feedback(feedback='Is Refuse')
        # Llama función restablecer cantidades a reclutar
        if self.state_type in ['in_progress','recruitment']:
            for rec in self.recruitment_requisition_line:
                rec.job_positions.reset_no_of_recruitment(rec.no_of_recruitment)

    # Function that creates assignee activity to track the request
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

    # Función que cierra la requisición
    def _compute_requisition_state_done(self):
        # mapping of stages created
        state_id = self.env['hr_requisition_state'].search([('state_type','=','done'),('recruitment_type_id','in',self.recruitment_type_id.ids)],
                                                           order="id asc", limit=1)
        c = 0
        for rec in self.recruitment_requisition_line:
            if rec.recruited == 'not_recruited':
                c += 1
        if c == 0:
            self.write({'state': state_id.id})

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    #   Conteo de etapas
    def _compute_stage_after2(self):
        stage_lines = []
        for rec in self.recruitment_type_id.state_id:
            stage_lines.append(str(rec.sequence))
            range = len(stage_lines)
        if int(range)-1 > self.state_level:
            self.state_level = self.state_level + 1
        self.state_after = self.env['hr_requisition_state'].search([('sequence','=',stage_lines[self.state_level])], limit=1)
        if self.manager_after_id:
            self.manager_id = self.manager_after_id
        else:
            self.manager_id = self.state.manager_id
        if self.time_off == 'Ausente':
            self.manager_id2 = self.state.optional_manager_id
            self.manager_before = self.state.optional_manager_id
        elif self.time_off == 'Disponible':
            self.manager_id2 = self.state.optional_manager_id
            self.manager_before = self.state.manager_id

    def button_action_on_aprobation2(self):
        if self.state_after.requires_approval == 'yes':
            if self.manager_after_id:
                user = self.manager_after_id.user_id
            else:
                user = self.state.manager_id.user_id
            note = 'Ha sido asignado para validar la siguiente solicitud.'
            # Código que crea una nueva actividad
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Validación RRHH Ticket',
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

    def compute_next_stage2(self):
        # if self.recruitment_type_id != 0:
        self.write({'state': self.state_after.id})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')
        self.button_action_on_aprobation2()
        self._compute_stage_after2()
        # Validación de puesto de trabajo en reclutamiento
        self.compute_constraints_job_id()

    def button_action_confirm2(self):
        if self.recruitment_requisition_line or self.recruitment_type != '0':
            if self.state_type == 'draft':
                self.compute_next_stage2()
            else:
                raise UserError('Debe estar en una etapa de estado borrador para poder confirmar.')
        else:
            raise UserError('No existe una linea de orden de reclutamiento')

#   Wizard Open
    def open_stage_transition_wizard2(self):
        new_wizard = self.env['hr_recruitment_requisition_stage_transition_wizard'].create({
            'hr_recruitment_requisition_id': self.id,
            'stage_id': self.state.id,
            'requires_approval': self.state_after.requires_approval,
            'manager_id': self.manager_before.id,
            'manager_after_id': self.state_after.manager_id.id,
            'recruitment_type_id': self.recruitment_type_id.id,
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
                                   ('recruitment', 'Recruitment'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='state.state_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions'),
                                         ('2', 'Labor dismissal'),
                                         ('3', 'Disciplinary Process')],
                                        string=r'Recruitment Type', index=True,
                                        related='recruitment_requisition_id.recruitment_type')
    contract_addendum = fields.Selection([('signed', 'Signed'), ('not_signed', 'Not signed'), ],
                                         string='Contract Addendum', default='not_signed', index=True,
                                         compute='_compute_contract_addendum')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # ///////////////////////////////////////  Recruitment  ////////////////////////////////////////////////////////

    job_positions = fields.Many2one(comodel_name='hr.job', string="Job Positions")
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

    # Creation function to write sections and notes
    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(job_positions=False, estimated_date_admission=False, recruited=False,
                          contract_type_id=False, contract_duration_qty=0)
        line = super(RecruitmentRequisitionLine, self).create(values)
        return line

    # Writing function to write sections and notes
    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                "You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type.")
        result = super(RecruitmentRequisitionLine, self).write(values)
        return result

    @api.onchange('job_positions')
    def _compute_estimated_date_admission(self):
        for rec in self:
            rec.estimated_date_admission = rec.recruitment_requisition_id.estimated_date_admission

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

    # Indicates if you are recruited
    @api.depends('job_positions')
    def _compute_job_positions(self):
        for rec in self:
            if rec.no_of_recruitment == rec.count_recruited:
                rec.recruited = 'recruited'
                rec.recruitment_requisition_id._compute_requisition_state_done()
            else:
                rec.recruited = 'not_recruited'
                rec.recruitment_requisition_id._compute_requisition_state_done()

    # Indicates if the other was signed if
    @api.depends('job_positions')
    def _compute_contract_addendum(self):
        for rec in self:
            if rec.no_of_recruitment == rec.count_recruited:
                rec.contract_addendum = 'signed'
            else:
                rec.contract_addendum = 'not_signed'








