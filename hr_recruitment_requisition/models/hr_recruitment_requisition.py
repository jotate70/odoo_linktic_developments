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
    state = fields.Many2one(comodel_name="hr_requisition_state", string="Stage", group_expand="_read_group_state_ids",
                            default=_get_default_state_id, tracking=True, ondelete="restrict", index=True, copy=False)
    state_blanket_order = fields.Many2one(comodel_name="hr_requisition_state", compute='_set_state')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True,
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
    requisition_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions')],
                                        string=r'Requisition Type', default='single_requisition', index=True,
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
    assigned_id = fields.Many2one(comodel_name='res.users', string='Asignado', store=True, readonly=False, tracking=True,
                                  domain=lambda self: [('groups_id', 'in', self.env.ref('hr.group_hr_manager').id)])
    activity_assigned_id = fields.Integer(string='Assigned activity')
    # Recruitment fields
    budget_post_id = fields.Many2one(comodel_name='account.budget.post', string='Budgetary Position',
                                     domain="[('is_payroll_position', '=', True)]")
    budget_value = fields.Float(string='Budget Value')
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type")
    contract_duration_qty = fields.Char(string='Contract qty')
    contract_duration_sel = fields.Selection(selection=[('weekly', 'Weekly'),
                                                        ('month', 'Month'),
                                                        ('annual', 'Annual')],
                                              string="Contract Duration", default='month', tracking=True)
    working_modality = fields.Selection(selection=[('mixed', 'Mixed'),
                                                   ('in_person', 'In Person'),
                                                   ('remote', 'Remote')],
                                        string="Working Modality", tracking=True, copy=False)
    working_time = fields.Selection(selection=[('half', 'Half Time'),
                                               ('full', 'Full Time'),
                                               ('deliverables', 'Defined by deliverables')],
                                    string="Working Time", tracking=True, copy=False)
    profile_attachments_ids = fields.One2many(comodel_name='ir.attachment', inverse_name='hr_recruitment_requisition_id',
                                           string="Profile Attachments", tracking=True)
    count_attachments = fields.Integer(string='Aplicaciones', compute='_compute_count_attachments')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Account Analytic',
                                          check_company=True)

    # @api.onchange('assigned_id')
    def _select_activity_assigned_id(self):
        if self.state_type in ['confirm', 'in_progress']:
            note = ''; summary = ''
            if self.requisition_type == '0':
                summary = 'Solicitud de seleccion y contratacion de personal'
                note = 'Ha sido asignado para realizar seguimiento en el proceso de seleccion y contratacion de personal.'
            elif self.requisition_type == '1':
                summary = 'Solicitud modificacion de condiciones laborales'
                note = 'Ha sido asignado para realizar seguimiento en el proceso, modificacion de condiciones laborales.'
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

    @api.onchange('employee_id')
    def create_recruitment_type_id(self):
        c = 0
        V = ['Single New', 'Replacement by voluntary withdrawal/Replacement by mutual agreement', 'Ascent/Transfer']
        V1 = ['0', '1', '2']
        V2 = ['single_requisition', 'multiple_requisition', 'multiple_requisition']
        data = self.env['hr_recruitment_type'].search([('recruitment_type', 'in', V1)])
        if data:
            self.recruitment_type_id = data[0]
            return
        else:
            for rec in [0, 1, 2]:
                create_vals = {
                    'name': V[rec],
                    'contract_type_id': 1,
                    'recruitment_type': V1[rec],
                    'requisition_type': V2[rec],
                }
                vat = self.env['hr_recruitment_type'].sudo().create(create_vals)
                if rec == 0:
                    self.recruitment_type_id = vat

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

    # Seleciona los responsables de aprobaión inicial y departamento
    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        if self.employee_id and self.state_type == 'draft':
            self.manager_id = self.employee_id.hr_manager_id
            self.manager_id2 = self.state.optional_manager_id
            self.department_id = self.employee_id.department_id

    def button_action_confirm(self):
        if self.recruitment_requisition_line:
            if self.state_type == 'draft':
                # mapping of stages created
                state_id = self.env['hr_requisition_state'].search([('state_type','=','confirm')],
                                                                   order="id asc", limit=1)
                self.write({'state': state_id.id})
                self.manager_id = self.state.manager_id
                self.manager_id2 = self.state.optional_manager_id
                note = ''; summary=''
                if self.requisition_type == '0':
                    summary = 'Solicitud de seleccion y contratacion de personal'
                elif self.requisition_type == '1':
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
                    'summary': 'Solicitud de requisición de personal:',
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
            else:
                raise UserError('Debe estar en estado borrador para poder confirmar.')
        else:
            raise UserError('No heciste una linea de orden de reclutamiento')

    def button_action_on_aprobation(self):
        if self.recruitment_requisition_line:
            if self.manager_before.user_id == self.env.user:
                if self.ceo == 'no' and (self.recruitment_type_id.recruitment_type in ['0', '2'] or (self.recruitment_type_id.recruitment_type == '1' and self.manager_id2.department_id.ceo == 'no')):
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Validación de disponibilidad de manager_id
                    if self.time_off == 'Ausente':
                        user = self.manager_before.parent_id.parent_id.user_id.id
                        note = 'Ha sido asignado para aprobar la siguiente requisición de personal, El gerente responable se encuentra ausente'
                        self.write({'manager_id': self.manager_before.parent_id.id,
                                    'manager_id2': self.manager_before.parent_id.parent_id.id,
                                    'manager_before': self.manager_before.parent_id.parent_id.id})
                    elif self.time_off == 'Disponible':
                        user = self.manager_before.parent_id.user_id.id
                        note = 'Ha sido asignado para aprobar la siguiente requisición de personal'
                        self.write({'manager_id': self.manager_before.parent_id.id,
                                    'manager_id2': self.manager_before.parent_id.parent_id.id,
                                    'manager_before': self.manager_before.parent_id.id})
                    # Código que crea una nueva actividad
                    model_id = self.env['ir.model']._get(self._name).id
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de requisición de personal:',
                        'automated': True,
                        'note': note,
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': model_id,
                        'res_id': self.id,
                        'user_id': user,
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                    #self.write({'manager_id': self.manager_id2.id})
                    #self.write({'manager_id2': self.manager_id.parent_id.id})
                    # Contador
                    c = self.state_aprove + 1
                    self.write({'state_aprove': c,
                                'state': 'on_aprobation'})
                elif self.ceo == 'yes' or (self.recruitment_type_id.recruitment_type == '1' and self.manager_id2.department_id.ceo == 'yes'):
                    self.write({'state': 'approved'})
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Resetear contador
                    self.write({'state_aprove': 0})
                    # Llama función actulizar cantidades a reclutar
                    for rec in self.recruitment_requisition_line:
                        rec.job_positions.update_no_of_recruitment(rec.no_of_recruitment)
            else:
                raise UserError('El gerente responsable debe aprobar la solicitud.')
        else:
            raise UserError('No heciste una linea de orden de reclutamiento')

    def button_action_done(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'done')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'priority': '0'})

    def button_action_draft(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'draft')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    'name': 'New',
                    'priority': '0',
                    'state_aprove': 0})
        # Responsables iniciales
        self._compute_select_manager_id()

    def button_action_cancel(self):
        state_id = self.env['hr_requisition_state'].search([('state_type', '=', 'refused')],
                                                           order="id asc", limit=1)
        self.write({'state': state_id.id,
                    # 'manager_id': self.department_id.manager_id.id,
                    # 'manager_id2': self.department_id.manager_id.parent_id.id,
                    'priority': '0',
                    'state_aprove': 0,
                    'manager_before': False})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Is Refuse')
        # Llama función restablecer cantidades a reclutar
        if self.state_type == 'in_progress':
            for rec in self.recruitment_requisition_line:
                rec.job_positions.reset_no_of_recruitment(rec.no_of_recruitment)

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
        """Creates a new wizard that will add a log with the results of the ticket stage, computes the valid stages
        for the next step in the process flow configured on helpdesk_stage_category_relation model"""
        # actual_stage_category_relation = self.env['helpdesk.stage.category.relation'].search(
        #     [('sequence', '=', self.stage_sequence), ('category_id', '=', self.category_id.id),
        #      ('stage_id', '=', self.stage_id.id)])

        # if actual_stage_category_relation.approver_user_ids and not self.stage_approve:
        #     raise ValidationError(_("Cannot End this stage without the needed approval"))

        # stage_category_relations = self.env['helpdesk.stage.category.relation'].search(
        #     [('sequence', '=', self.state_aprove + 1), ('category_id', '=', self.recruitment_type_id.id)])

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

    state = fields.Many2one(comodel_name="hr_requisition_state", string="Stage", related='recruitment_requisition_id.state')
    state_type = fields.Selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('in_progress', 'In Progress'),
                                   ('done', 'Done'),
                                   ('refused', 'Refused')],
                                  string='State Type', store=True, related='state.state_type',
                                  help='classifies the type of stage, important for the behavior of the approval for personnel request.')
    recruitment_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition', string='Recruitment Requisition')
    # job_positions_domain = fields.Char(string='Job Domain', compute='_domain_job_positions_domain')
    job_positions_domain = fields.Char(string='Job Domain')
    job_positions = fields.Many2one(comodel_name='hr.job', string="Job Positions", required=True)
    job_positions_after = fields.Many2one(comodel_name='hr.job', string="new job")
    no_of_recruitment = fields.Integer(string='New Employees',
                                       help='Number of new employees you expect to recruit.', default=1)
    estimated_date_admission = fields.Date(string='Entry date estimated', readonly=False, select=True)
    recruited = fields.Selection([('recruited', 'Recruited'), ('not_recruited', 'Not Recruited'),],
                                 string='Recruited', default='not_recruited', index=True, compute='_compute_job_positions')
    contract_addendum = fields.Selection([('signed', 'Signed'), ('not_signed', 'Not signed'),],
                                 string='Contract Addendum', default='not_signed', index=True, compute='_compute_contract_addendum')
    count_recruited = fields.Integer(string='Recruited Employees', compute='_compute_count_recruited')
    observations = fields.Text(string='Observations')
    state_contract = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status Contract', tracking=True, help='Status of the contract')
    recruitment_type = fields.Selection([('0', 'recruitment'),
                                         ('1', 'modifications of working conditions')],
                                        string=r'Recruitment Type', index=True,
                                        related='recruitment_requisition_id.recruitment_type')
    # employee_domain = fields.Char(string='Employee Domain', compute='_domain_employee_id')
    employee_domain = fields.Char(string='Employee Domain')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    wage = fields.Float('Wage', tracking=True, help="Employee's monthly gross wage.")
    contract_id = fields.Many2one(comodel_name='hr.contract', string='Current Contract')
    date_end = fields.Date('End Date', tracking=True,
                           help="End date of the contract (if it's a fixed-term contract).")

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
                a.append(rec2.job_title_2.id)
                for rec3 in rec2.child_ids:
                    a.append(rec3.job_title_2.id)
            jon_title = rec.env['hr.employee'].sudo().search(
                [('active', '=', True), ('active', '=', False), ('job_title_2', 'in', a)])
            employee = rec.env['hr.job'].sudo().search(
                [('id', 'in', jon_title.ids)])
            if employee:
                rec.job_positions_domain = json.dumps(['|',('id', 'in', employee.ids),
                                                       ('id','=',rec.env.user.employee_id.job_title_2.ids)])
            else:
                rec.job_positions_domain = json.dumps([])

    # # function domain dynamic
    # @api.onchange('job_positions')
    # @api.depends('employee_id')
    # def _domain_employee_id(self):
    #     for rec in self:
    #         employee = rec.env['hr.employee'].sudo().search([('job_title_2', 'in', rec.job_positions.ids), '|', ('active', '=', True), ('active', '=', False)])
    #         if employee:
    #             rec.employee_domain = json.dumps([('id', 'in', employee.ids), '|', ('active', '=', True), ('active', '=', False)])
    #         else:
    #             rec.employ1ee_domain = json.dumps([()])

    @api.onchange('employee_id')
    def _compute_contract_wage(self):
        for rec in self:
            contract = rec.env['hr.contract'].sudo().search(
                [('employee_id', '=', rec.employee_id.ids), ('state', 'in', ['cancel', 'close', 'open'])], limit=1)
            rec.wage = contract.wage
            rec.contract_id = contract
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








