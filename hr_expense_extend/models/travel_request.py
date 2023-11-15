# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class travel_expence(models.Model):
    _name = "travel.expence"

    product_id = fields.Many2one(comodel_name='product.product', string="Product", domain=[('can_be_expensed', '=', True)], required=True)
    unit_price = fields.Float(string="Unit Price", required=True)
    product_qty = fields.Float(string="Quantity", required=True)
    name = fields.Char(string="Expense Note")
    currency_id = fields.Many2one(comodel_name='res.currency', string="Moneda")
    
class My_travel_request(models.Model):
    _name = "travel.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Solicitud de viajes"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, readonly=False,
                                 default=lambda self: self.env.company)
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', required=True, string="Cuenta Analítica")
    hr_travel_info_ids = fields.One2many(comodel_name='hr_travel_info', inverse_name='travel_request_id')
    hr_hotel_info_ids = fields.One2many(comodel_name='hr_hotel_info', inverse_name='travel_request_id')
    priority = fields.Selection(
        [('0', 'All'),
         ('1', 'Low priority'),
         ('2', 'High priority'),
         ('3', 'Urgent')], string='Prioridad', default='0', index=True)
    name = fields.Char(string="Name", readonly=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Empleado", required=True, default=lambda self: self.env.user.employee_id.id)
    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id, readonly=True)

    request_by = fields.Many2one(comodel_name='hr.employee', string="Solicitado por", default=lambda self: self.env.user.employee_id.id)
    confirm_by = fields.Many2one(comodel_name='res.users', string="Confirmado por")
    approve_by = fields.Many2one(comodel_name='res.users', string="Aprobado por")

    req_date = fields.Date(string="Fecha de solicitud")
    confirm_date = fields.Date(string="Fecha de confirmación")
    approve_date = fields.Date(string="Fecha de aprobación")
    # expence_sheet_company_id = fields.Many2one(comodel_name='hr.expense.sheet', string="Hoja de anticipo creada",
    #                                            readonly=True)
    # expence_sheet_id = fields.Many2one(comodel_name='hr.expense.sheet', string="Hoja de reembolso creada", readonly=True)
    #
    expence_sheet_advance_ids = fields.One2many(comodel_name='hr.expense.sheet', inverse_name='travel_request1_id',
                                                string="Legalización de gastos")
    count_sheet_advance = fields.Integer(string='Count advances', compute='_compute_count_sheet_advance')
    expence_sheet_own_ids = fields.One2many(comodel_name='hr.expense.sheet', inverse_name='travel_request2_id',
                                            string="legalización de reembolso")
    count_sheet_own = fields.Integer(string='Count own', compute='_compute_count_sheet_own')
    #
    travel_mode_id = fields.Selection([('0', 'Nacional'),
                                       ('1', 'Internacional')], default='0', index=True, string='Tipo de viaje')
    return_mode_id = fields.Many2one(comodel_name='travel.mode', string="Modo de viaje de regreso")

    phone_no = fields.Char(string='Número de contacto')
    email = fields.Char(string='Correo electrónico')

    available_departure_date = fields.Date(string="Fecha de salida", required=True)
    available_return_date = fields.Date(string="Fecha de regreso", required=True)
    days = fields.Char(string='Días', compute="_compute_days")
    days2 = fields.Char(string='Días', compute="_compute_days2")
    identification_id = fields.Char(string='Número identificación', groups="hr.group_hr_user", tracking=True)
    passport_id = fields.Char(string='Número de pasaporte', groups="hr.group_hr_user", tracking=True)

    advance_payment_ids = fields.One2many(comodel_name='hr.expense', inverse_name='travel_id', string="Reporte de gastos")
    expense_ids = fields.One2many(comodel_name='hr.expense', inverse_name='travel_expence_id', string="Gastos")

    state = fields.Selection([('draft', 'Borrador'),
                              ('confirmed', 'Confirmado'),
                              ('on_aprobation', 'En aprobación'),
                              ('approved', 'Anticipo Aprobado'),
                              ('paid_advance', 'Legalización'),
                              ('submitted', 'Gastos Reportados'),
                              ('rejected', 'Rechazado'),
                              ],
                             default="draft", string="Estado")

    # extras fields
    activity_id = fields.Integer(string='id actividad')
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Gerente responsable',
                                 help='Responsable de aprobación')
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    state_aprove = fields.Integer(string='approval level')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otros')
    ], groups="hr.group_hr_user", tracking=True, string='Género')
    visa_country_id = fields.Many2one(comodel_name='res.country', string="País de la visa")
    visa_no = fields.Char(string='Número de visa', groups="hr.group_hr_user", tracking=True)
    visa_expire = fields.Date(string='Fecha de vencimiento de la visa', groups="hr.group_hr_user",
                              tracking=True)
    permit_no = fields.Char(string='Número de permiso de trabajo', groups="hr.group_hr_user",
                            tracking=True)
    emergency_contact = fields.Char(string="Contacto de emergencia", groups="hr.group_hr_user",
                                    tracking=True)
    emergency_phone = fields.Char(string="Teléfono de emergencia", groups="hr.group_hr_user",
                                  tracking=True)
    financial_manager = fields.Many2one(comodel_name='hr.employee', string='Gerente Financiero', related='company_id.financial_manager')
    birthday = fields.Date(string='Fecha de nacimiento')
    # Aditional fields
    general_manager = fields.Many2one(comodel_name='hr.employee', string='Vicepresidente', related='company_id.general_manager')
    purchase_request_ids = fields.One2many(comodel_name='purchase.request',
                                           inverse_name='travel_request_id',
                                           string='Requisiciones')
    count_purchase_request = fields.Integer(string='Count Purchase Request', compute='_compute_count_purchase_request')
    expense_advance_ids = fields.One2many(comodel_name='hr.expense.advance', inverse_name='travel_request_id', string="Anticipos")
    job_type = fields.Selection([('president', 'Presidente'),
                                 ('vice_president', 'Vicepresidente'),
                                 ('director', 'Director'),
                                 ('department_manager', 'Gerente Procesos'),
                                 ('project_manager', 'Gerente Proyectos'),
                                 ('operational_staff', 'Personal Operativo')],
                                string='Tipo de cargo', related='manager_id.job_id.job_type')
    count_approved = fields.Integer(string='Contador de aprovaciones')
    general_budget_id = fields.Many2one(comodel_name='account.budget.post', string='Budgetary Position')
    budget_line_segregation_id = fields.Many2one(comodel_name='crossovered.budget.lines.segregation',
                                                 string='Budget Line Segregation',
                                                 domain="[('general_budget_id', '=?', general_budget_id), ('analytic_account_id', '=?', account_analytic_id)]")
    segregation_balance = fields.Monetary(string="Balance", compute="get_segregation_balance", store=True, readonly=True)

    def compute_expense_advance_paid(self):
        if self.state == 'approved' and self.financial_manager == self.env.user.employee_id:
            c = 0
            for rec in self.expense_advance_ids:
                if rec.state != 'to_pay':
                    c += 1
            if c == 0:
                self.state = 'paid_advance'
            else:
                raise UserError('Porfavor pagar los anticipos para continuar')
        else:
            raise UserError('Solo el gerente financiero puede validar')

    @api.depends('budget_line_segregation_id')
    def get_segregation_balance(self):
        for record in self:
            if record.budget_line_segregation_id:
                record.segregation_balance = (record.budget_line_segregation_id.planned_amount - record.budget_line_segregation_id.practical_amount) * -1
            else:
                record.segregation_balance = 0

    def _compute_count_purchase_request(self):
        if self.purchase_request_ids:
            for rec in self.purchase_request_ids:
                self.count_purchase_request += 1
        else:
            self.count_purchase_request = 0

    def _compute_count_sheet_advance(self):
        if self.expence_sheet_advance_ids:
            for rec in self.expence_sheet_advance_ids:
                self.count_sheet_advance += 1
        else:
            self.count_sheet_advance = 0

    def _compute_count_sheet_own(self):
        if self.expence_sheet_own_ids:
            for rec in self.expence_sheet_own_ids:
                self.count_sheet_own += 1
        else:
            self.count_sheet_own = 0

      # Anticpos automaticos
    def _compute_generate_expense_advance_ids(self):
        employee = []
        for rec in self.hr_travel_info_ids.employee_ids:
            employee.append(rec.id)
            for rec2 in self.hr_hotel_info_ids.employee_ids:
                employee.append(rec2.id)
        self.demo = set(employee)
        # for rec3 in employee:
        #     product = rec.env['product.product'].search([('product_expense_type', '=', 'advance')], limit=1)
        #     amount = rec.env['hr_type_travel_expenses'].search([('product_id', '=', rec.product_id.ids),
        #                                                         ('currency_id', '=', rec.currency_id.ids)], limit=1)
        #     if amount:
        #         if rec.employee_id.job_id.job_type == 'president':
        #             value = amount.amount_president
        #         elif rec.employee_id.job_id.job_type == 'vice_president':
        #             value = amount.amount_vice_president
        #         elif rec.employee_id.job_id.job_type == 'director':
        #             value = amount.amount_director
        #         elif rec.employee_id.job_id.job_type == 'department_manager':
        #             value = amount.amount_department_manager
        #         elif rec.employee_id.job_id.job_type == 'project_manager':
        #             value = amount.amount_project_manager
        #         elif rec.employee_id.job_id.job_type == 'operational_staff':
        #             value = amount.amount_operational_staff
        #     else:
        #     create_vals = {
        #         'employee_id': rec3,
        #         'date': self.available_departure_date,
        #         'travel_request_id': self.id,
        #         'product_id': product,
        #         'days': self.days,
        #         'days2': self.days2,
        #         'amount_qty': amount,
        #         'total_amount': amount * int(self.days2),
        #         'account_id': self.employee_id.company_id.hr_expense_advance_account.id,
        #         'analytic_account_id': self.account_analytic_id.id,
        #         # 'journal_id':,
        #         'company_id': self.employee_id.company_id.id,
        #     }
        #     self.env['mail.activity'].create(create_vals)

    @api.depends('available_departure_date','available_return_date')
    def _compute_days(self):
        for line in self:
            line.days = False
            if line.available_departure_date and line.available_return_date:
                diff = line.available_return_date- line.available_departure_date
                mini = diff.seconds // 60
                hour = mini // 60
                sec = (diff.seconds) - (mini * 60)
                miniute = mini - (hour * 60)
                time = str(diff.days) + ' Days'
                line.days = time
                return
            else:
                line.days = 0
                return

    @api.depends('available_departure_date', 'available_return_date')
    def _compute_days2(self):
        for line in self:
            line.days = False
            if line.available_departure_date and line.available_return_date:
                diff = line.available_return_date- line.available_departure_date
                line.days2 = diff.days

    @api.onchange('supplier_id')
    def _raise_financial_manager_supplier(self):
        if self.financial_manager:
            return
        else:
            raise UserError('Debes agregar responsable financiero al empleado.')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('travel.request') or '/'
        vals['name'] = seq
        vals['request_by'] = vals['employee_id']
        vals['req_date'] = fields.datetime.now()
        return super(My_travel_request, self).create(vals)

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

    # Seleciona los responsables de aprobaión inicial y departamento
    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id and self.state in ['draft']:
            self.manager_id = self.financial_manager
            self.identification_id = self.employee_id.identification_id
            self.passport_id = self.employee_id.passport_id
            self.gender = self.employee_id.gender
            self.visa_country_id = self.employee_id.visa_country_id
            self.visa_no = self.employee_id.visa_no
            self.visa_expire = self.employee_id.visa_expire
            self.permit_no = self.employee_id.permit_no
            self.emergency_contact = self.employee_id.emergency_contact
            self.emergency_phone = self.employee_id.emergency_phone
            self.birthday = self.employee_id.birthday
            return

    def action_expence_sheet(self):
        return {
            'name': 'Expense',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {},
            'res_model': 'hr.expense',
            'domain': [('id', 'in', self.expense_ids.ids)],
        }

    def action_expence_company_sheet(self):
        return {
            'name': 'Expense',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {},
            'res_model': 'hr.expense',
            'domain': [('id', 'in', self.advance_payment_ids.ids)],
        }

    def action_confirm(self):
        if self.state == 'draft':
            self._raise_financial_manager_supplier()
            if self.hr_travel_info_ids:
                self.write({'state': 'confirmed'})
                for rec in self.expense_advance_ids:
                    rec.button_to_approve()     # Confirmar anticipo
                # Código que crea una nueva actividad
                create_vals = {
                    'activity_type_id': 4,
                    'summary': 'Solicitud de viaje:',
                    'automated': True,
                    'note': 'Ha sido asignado para aprobar la siguiente solcitud de viaje.',
                    'date_deadline': fields.datetime.now(),
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                    'res_id': self.id,
                    'user_id': self.financial_manager.user_id.id,
                }
                new_activity = self.env['mail.activity'].create(create_vals)
                # Escribe el id de la actividad en un campo
                self.write({'activity_id': new_activity})
                # Contador de niveles de aprobación
                c = self.state_aprove + 1
                self.write({'state_aprove': c})
                self.confirm_by = self.env.user
            else:
                raise UserError('No se han agregado viajes a su solicitud')
        else:
            raise UserError('Debe estar en estado borrador para poder confirmar.')

    # Approve acción
    def button_action_on_aprobation(self):
        if self.hr_travel_info_ids:
            if  self.env.user in [self.financial_manager.user_id, self.general_manager.user_id]:
                if self.financial_manager == self.env.user.employee_id and self.count_approved == 0:
                    self.state_aprove += 1
                    self.count_approved += 1
                    self.write({'state': 'on_aprobation'})
                    self.manager_id = self.general_manager
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Código que crea una nueva actividad
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de viaje:',
                        'automated': True,
                        'note': 'Ha sido asignado para validar anticipo para solitud de viaje',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': self.env['ir.model']._get(self._name).id,
                        'res_id': self.id,
                        'user_id': self.general_manager.user_id.id,
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                elif self.general_manager == self.env.user.employee_id and self.count_approved == 1:
                    self.action_approve()
                    self.expense_advance_ids.sudo().button_approve()      # Aprobar anticipo
                    self.manager_id = self.financial_manager
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Código que crea una nueva actividad
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de viaje:',
                        'automated': True,
                        'note': 'Ha sido asignado para hacer seguimiento a la solitud de viaje',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': self.env['ir.model']._get(self._name).id,
                        'res_id': self.id,
                        'user_id': self.financial_manager.user_id.id,
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                    #  Creación de requisiciones
                    self._action_travel_expense_to_purchase_request()
                    self._action_hotel_expense_to_purchase_request()
                else:
                    raise UserError('Ya aprobastes la solicitud de viaje.')
            else:
                raise UserError('El gerente responsable debe aprobar la solicitud de viaje.')
        else:
            raise UserError('No se han agregado viáticos a la solicitud de viaje')

    def action_approve(self):
        self.write({'state': 'approved', 'approve_date': fields.datetime.now(), 'approve_by': self.env.user.id})
        return

    def action_draft(self):
        # Restablecer
        self.write({'state': 'draft'})
        self.state_aprove = 0
        self.count_approved = 0
        self.onchange_employee()
        # Restrablecer anticipo
        for rec in self.expense_advance_ids:
            rec.button_draft()
        return

    def action_reject(self):
        self.write({'state': 'rejected'})
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Solicitud Cancelada')
        self.expense_advance_ids.button_reject()  # cancelar anticipo
        # cancelar requisiciones
        for rec in self.purchase_request_ids:
            rec.button_rejected()
        return

    #   Compute function expense   NEW CODE
    def _compute_create_expense_sheet(self):
        if self.expense_advance_ids:
            for rec in self.expense_advance_ids:
                self.action_create_expense(rec.employee_id.id)

    def action_create_expense(self, employee):
        id_lst = []
        id_lst2 = []
        if self.expense_ids:
            for line1 in self.expense_ids:
                if line1.employee_id.id == employee:
                    id_lst.append(line1.id)
                res = self.env['hr.expense.sheet'].create({'name': self.env['ir.sequence'].next_by_code('expense.ifpv') or 'New', 'employee_id': employee,
                                                           'travel_expense': True, 'payment_mode': 'own_account', 'expense_line_ids' : [(6, 0, id_lst)]})
                # self.expence_sheet_id = res.id
                self.write({'expence_sheet_own_ids': [(4, res.id)]})
                self.write({'state': 'submitted'})
                id_lst2 = []
        if self.advance_payment_ids:
            for line2 in self.advance_payment_ids:
                if line2.employee_id.id == employee:
                    id_lst2.append(line2.id)
            res2 = self.env['hr.expense.sheet'].create(
                {'name': self.env['ir.sequence'].next_by_code('expense.ifpv') or 'New', 'employee_id': employee,
                 'travel_expense': True, 'payment_mode': 'company_account', 'expense_line_ids': [(6, 0, id_lst2)]})
            # self.expence_sheet_company_id = res2.id
            self.write({'expence_sheet_advance_ids': [(4, res2.id)]})

    def action_create_expense_refund(self):
        c = 0
        for a in self.expense_ids:
            if a.of_refunded == True:
                c += 1
        if c > 0:
            raise UserError('Ya existen diferencia de gasos a reembolsar, para volver a generar gastos a reembolsar elimine los existentes.')
        else:
            for rec in self.advance_payment_ids:
                if rec.total_amount < rec.actual_amount:            # New code
                    self.write({'expense_ids': [(0, 0, {'company_currency_id': self.currency_id.id,
                                                        'date': rec.date,
                                                        'product_id': rec.product_id.id,
                                                        'name': str(rec.name) + ', ' + str('diferencia a reembolsar'),
                                                        'employee_id': self.employee_id.id,
                                                        'sheet_id': rec.sheet_id.id,
                                                        #'payment_mode': 'own_account',
                                                        'activity_ids': rec.activity_ids.id,
                                                        'reference': rec.reference,
                                                        'accounting_date': rec.accounting_date,
                                                        'analytic_account_id': rec.analytic_account_id.id,
                                                        # 'analytic_tag_ids': rec.analytic_tag_ids,
                                                        'account_id': rec.account_id.id,
                                                        'company_id': rec.company_id.id,
                                                        'unit_amount': rec.unit_amount,
                                                        'quantity': rec.quantity,
                                                        'tax_ids': rec.tax_ids.id,
                                                        'attachment_number': rec.attachment_number,
                                                        'total_amount': abs(rec.total_amount - rec.actual_amount),
                                                        'currency_id': rec.currency_id.id,
                                                        'message_unread': rec.message_unread,
                                                        'of_refunded': rec.of_refunded,
                                                        'supplier_id': rec.supplier_id.id,
                                                        'supplier_type': rec.supplier_type.id,
                                                        'supplier_vat': rec.supplier_vat,
                                                        })]})

    def _action_travel_expense_to_purchase_request(self):
        for rec in self.hr_travel_info_ids:
            self.write({'purchase_request_ids': [(0, 0, {'travel_request_id': self.id,
                                                         'hr_travel_info_id': rec.id,
                                                         'state': 'draft',
                                                         'requested_by': self.employee_id.user_id.id,
                                                         'origin': self.name,
                                                         'date_start': self.approve_date,
                                                         'company_id': self.company_id.id,
                                                         'description': rec.name,
                                                         'line_ids': [(0, 0, {'product_id': rec.product_id.id,
                                                                              'name': self.approve_date,
                                                                              'product_qty': rec.passengers,
                                                                              'product_uom_id': 1,
                                                                              'analytic_account_id': rec.account_analytic_id.id,
                                                                              })]
                                                        })]})

    def _action_hotel_expense_to_purchase_request(self):
        for rec in self.hr_hotel_info_ids:
            self.write({'purchase_request_ids': [(0, 0, {'travel_request_id': self.id,
                                                         'hr_hotel_info_id': rec.id,
                                                         'state': 'draft',
                                                         'requested_by': self.employee_id.user_id.id,
                                                         'origin': self.name,
                                                         'date_start': self.approve_date,
                                                         'company_id': self.company_id.id,
                                                         'description': rec.name,
                                                         'line_ids': [(0, 0, {'product_id': rec.product_id.id,
                                                                              'name': self.approve_date,
                                                                              'product_qty': rec.number_people,
                                                                              'product_uom_id': 1,
                                                                              'analytic_account_id': rec.account_analytic_id.id,
                                                                              })]
                                                        })]})

class my_travel_request(models.Model):
    _name = "travel.mode"

    name = fields.Char('Travel Mode')


