from odoo import fields, _, models, api
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression

class HrExpenseAdvance(models.Model):
    _name = "hr.expense.advance"
    _description = "HR Expense Advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_employee_id(self):
        employee = self.env.user.employee_id
        if not employee and not self.env.user.has_group('hr_expense.group_hr_expense_team_approver'):
            raise ValidationError(_('The current user has no related employee. Please, create one.'))
        return employee

    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)]  # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups(
                'account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False),
                   ('company_id', '=', employee.company_id.id)]
        return res

    activity_id = fields.Integer(string='id actividad')
    state_aprove = fields.Integer(string='approval level')
    count_approved = fields.Integer(string='Contador de aprovaciones')
    parent_id = fields.Many2one(comodel_name='hr.employee', string='Jefe inmediato',
                                related='employee_id.parent_id')
    manager_id = fields.Many2one(comodel_name='res.users', string='Aprobador', store=True,
                                 help='Responsable de aprobación')
    name = fields.Char(string='Advance No.', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Date(default=fields.Date.context_today, string="Advance Date")
    employee_id = fields.Many2one(comodel_name='hr.employee', compute='_compute_employee_id', string="Employee",
                                  store=True, required=True, readonly=False, tracking=True,
                                  default=_default_employee_id,
                                  domain=lambda self: self._get_employee_id_domain(),
                                  check_company=True)
    total_amount = fields.Monetary(string="Total In Currency", currency_field='currency_id', tracking=True)
    company_currency_id = fields.Many2one(comodel_name='res.currency', string="Report Company Currency",
                                          related='company_id.currency_id', readonly=True)
    total_amount_company = fields.Monetary(string="Total", compute='_compute_total_amount_company', store=True,
                                           currency_field='company_currency_id')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account', check_company=True)
    analytic_tag_ids = fields.Many2many(comodel_name='account.analytic.tag', string='Analytic Tags',
                                        states={'post': [('readonly', True)], 'done': [('readonly', True)]},
                                        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    account_id = fields.Many2one(comodel_name='account.account', related='company_id.hr_expense_advance_account')
    description = fields.Text(string='Notes...', readonly=True,
                              states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                                      'refused': [('readonly', False)]})
    attachment_number = fields.Integer(string='Number of Attachments', compute='_compute_attachment_number')
    state = fields.Selection(selection=[('draft', 'To Submit'),
                                        ('to_approve', 'Submitted'),
                                        ('approved', 'Approved'),
                                        ('to_pay', 'Waiting Legalization'),
                                        ('done', 'Done'),
                                        ('refused', 'Refused')],
                             string='Status', copy=False, index=True, readonly=True, default='draft', help="Status of the advance.")
    sheet_id = fields.One2many(comodel_name='hr.expense.sheet', inverse_name='payment_advance_id', string='Expense Report', copy=False)
    sheet_count = fields.Integer(string='Sheet Count', compute='get_sheet_count')
    is_refused = fields.Boolean(string="Explicitly Refused by manager or accountant", readonly=True, copy=False)

    is_editable = fields.Boolean(string="Is Editable By Current User", compute='_compute_is_editable')
    same_currency = fields.Boolean(string="Is currency_id different from the company_currency_id",
                                   compute='_compute_same_currency')

    scheduled_payment_day = fields.Date(string='Scheduled Payment Date')
    payment_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Bank',
                                         domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    approved_manager = fields.Boolean(string='Approved Manager', default=False)

    account_move_id = fields.Many2one(comodel_name='account.move', string="Account Move Generated")
    journal_id = fields.Many2one(comodel_name='account.journal', string="Advance Journal",
                                 domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]")

    # change payment status from the bulk payment module
    def _compute_onchange_state(self):
        if self.state == 'approved' and self.account_move_id.payment_state == 'paid':
            self.state = 'to_pay'

    @api.onchange('employee_id')
    def _compute_select_manager_id(self):
        self.manager_id = self.employee_id.parent_id.user_id
        self.journal_id = self.company_id.journal_expense_advance_id

    # related approved manager in account move
    @api.onchange('approved_manager')
    def _compute_related_approved_manager_advance(self):
        for rec in self:
            rec.account_move_id.update({'scheduled_payment_day': rec.scheduled_payment_day,
                                        'payment_journal_id': rec.payment_journal_id.id,
                                        'payment_state': 'not_paid',
                                        'approved_manager': rec.approved_manager,
                                        'approved_date_payment': fields.datetime.now(),
                                        # 'hr_expense_advance_related_id': self.ids,
                                        })

    def get_sheet_count(self):
        for record in self:
            record.sheet_count = len(record.sheet_id.ids)

    @api.depends('currency_id', 'company_currency_id')
    def _compute_same_currency(self):
        for advance in self:
            advance.same_currency = bool(
                not advance.company_id or (advance.currency_id and advance.currency_id == advance.company_currency_id))

    @api.depends('date', 'total_amount', 'currency_id', 'company_currency_id')
    def _compute_total_amount_company(self):
        for advance in self:
            amount = 0
            if advance.same_currency:
                amount = advance.total_amount
            else:
                date_expense = advance.date or fields.Date.today()
                amount = advance.currency_id._convert(
                    advance.total_amount, advance.company_currency_id,
                    advance.company_id, date_expense)
            advance.total_amount_company = amount

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.expense.advance'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for advance in self:
            advance.attachment_number = attachment.get(advance._origin.id, 0)

    @api.depends('employee_id')
    def _compute_is_editable(self):
        is_account_manager = self.env.user.has_group('account.group_account_user') or self.env.user.has_group(
            'account.group_account_manager')
        for advance in self:
            if advance.state == 'draft' or advance.sheet_id.state in ['draft', 'submit']:
                advance.is_editable = True
            elif advance.sheet_id.state == 'approve':
                advance.is_editable = is_account_manager
            else:
                advance.is_editable = False

    # @api.constrains('approved_manager')
    # def _check_approved_manager_permissions(self):
    #     for advance in self:
    #         if not self.env.user.has_group('hr_expense.group_hr_expense_manager'):
    #             raise ValidationError(_("This user doesn't have approval permissions."))
    #         if advance.state not in ('approved', 'draft'):
    #             raise ValidationError(_("Only can change the Approval state of approved advances."))

    def write(self, vals):
        if 'approved_manager' in vals:
            if not self.env.user.has_group('hr_expense.group_hr_expense_manager'):
                raise ValidationError(_("This user doesn't have approval permissions."))

            if any(advance.state != 'approved'for advance in self):
                raise ValidationError(_("Only can change the Approval state of approved advances."))

        return super(HrExpenseAdvance, self).write(vals)

    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for advance in self:
                advance.employee_id = self.env.user.with_company(advance.company_id).employee_id

    # ----------------------------------------
    # ORM Overrides
    # ----------------------------------------

    @api.ondelete(at_uninstall=False)
    def _unlink_except_posted_or_approved(self):
        for advance in self:
            if advance.state in ['done', 'approved']:
                raise UserError(_('You cannot delete a posted or approved advance.'))

    # ----------------------------------------
    # Actions
    # ----------------------------------------

    def action_view_sheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.expense.sheet',
            'target': 'current',
            'res_id': self.sheet_id.id
        }

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'hr.advance'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.advance', 'default_res_id': self.id}
        return res

    # ----------------------------------------
    # Business
    # ----------------------------------------

    def _get_account_move_line_values(self, move_ref):
        self.ensure_one()
        lines_list = []
        employee_contact = self.employee_id.sudo().address_home_id.with_company(self.company_id)

        deb_line = {
            'name': move_ref,
            'account_id': self.company_id.property_account_advance_id.id,
            'debit': self.total_amount,
            'credit': 0.0,
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'currency_id': self.company_currency_id != self.currency_id and self.company_currency_id.id or False,
            'amount_currency': self.company_currency_id != self.currency_id and self.total_amount_company or 0.0,
            'partner_id': employee_contact.id,
        }
        lines_list.append((0, 0, deb_line))

        cred_line = {
            'name': move_ref,
            'account_id': self.company_id.hr_expense_advance_account.id,
            'debit': 0.0,
            'credit': self.total_amount,
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'currency_id': self.company_currency_id != self.currency_id and self.company_currency_id.id or False,
            'amount_currency': self.company_currency_id != self.currency_id and - 1.0 * self.total_amount_company or 0.0,
            'partner_id': employee_contact.id,
        }
        lines_list.append((0, 0, cred_line))

        return lines_list

    def _get_account_move_values(self):
        self.ensure_one()
        if not self.employee_id.sudo().address_home_id:
            raise UserError(
                _("No Home Address found for the employee %s, please configure one.") % (self.employee_id.name))
        move_ref = _("Expense Advance Journal Entry")
        move_vals = {
            'ref': move_ref,
            'date': fields.Date.today(),
            'journal_id': self.journal_id.id,
            'line_ids': self._get_account_move_line_values(move_ref),
            'name': '/',
            'move_type': 'entry',
            'currency_id': self.currency_id.id,
        }

        return move_vals

    def refuse_advance(self, reason):
        self.write({'is_refused': True})
        self.sheet_id.write({'state': 'cancel'})
        self.sheet_id.message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                             values={'reason': reason, 'is_sheet': False, 'name': self.name})

    # function that there are no advance payments in progress
    def _validate_advance_in_progress(self):
        for rec in self:
            data = 0
            validate = self.env['hr.expense.advance'].search([('employee_id', '=', rec.employee_id.ids), ('state', 'in', ['to_approve', 'approved', 'to_pay'])])
            data = len(validate)
            if data > 0:
                raise ValidationError(message=("El empleado '%s' cuenta con un anticipo en curso, finalice el proceso de anticipo para continuar", self.employee_id.name))

    def action_button_to_approve(self):
        if self.state == 'draft':
            self._validate_advance_in_progress()
            self.button_to_approve()
            self.manager_id = self.parent_id.user_id
            self.count_approved += 1
            self.state_aprove += 1
            # Código que crea una nueva actividad
            create_vals = {
                'activity_type_id': 4,
                'summary': 'Solicitud de viaje:',
                'automated': True,
                'note': 'Ha sido asignado para aprobar el siguiente anticipo',
                'date_deadline': fields.datetime.now(),
                'res_model_id': self.env['ir.model']._get(self._name).id,
                'res_id': self.id,
                'user_id': self.employee_id.parent_id.user_id.id,
            }
            new_activity = self.env['mail.activity'].create(create_vals)
            # Escribe el id de la actividad en un campo
            self.write({'activity_id': new_activity})
        else:
            raise UserError('Debe estar en estado "A enviar" para poder confirmar.')


    def button_to_approve(self):
        if self.name == _("New"):
            self.name = self.env["ir.sequence"].next_by_code("hr.expense.advance.sequence")
        return self.write({"state": "to_approve"})

    def button_draft(self):
        self.state_aprove = 0
        self.count_approved = 0
        return self.write({"state": "draft"})

    def action_button_approve(self):
        if self.state == 'to_approve':
            if self.env.user in [self.manager_id]:
                if self.manager_id == self.env.user and self.count_approved == 1:
                    self.state_aprove += 1
                    self.count_approved += 1
                    self.manager_id = self.company_id.financial_manager_id
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Código que crea una nueva actividad
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de viaje:',
                        'automated': True,
                        'note': 'Ha sido asignado para validar anticipo',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': self.env['ir.model']._get(self._name).id,
                        'res_id': self.id,
                        'user_id': self.company_id.financial_manager_id.id,
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                elif self.manager_id == self.env.user and self.count_approved == 2:
                    self.state_aprove += 1
                    self.count_approved += 1
                    self.write({'state': 'to_approve'})
                    self.manager_id = self.company_id.general_manager_id
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    # Código que crea una nueva actividad
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de viaje:',
                        'automated': True,
                        'note': 'Ha sido asignado para validar anticipo',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': self.env['ir.model']._get(self._name).id,
                        'res_id': self.id,
                        'user_id': self.company_id.general_manager_id.id,
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                elif self.manager_id == self.env.user and self.count_approved == 3:
                    #  Marca actividad como hecha de forma automatica
                    new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                    new_activity.action_feedback(feedback='Es Aprobado')
                    self.manager_id = self.company_id.account_manager_id
                    # Aprobación
                    self.button_approve()
                else:
                    raise UserError('Ya aprobastes el anticipo.')
            else:
                raise UserError('El gerente responsable debe aprobar el anticpo.')
        else:
            raise UserError('Debe estar en estado "Esperando Aprobación" para poder Aprobar.')

    def button_approve(self):
        for record in self:
            new_move = self.env['account.move'].create(record._get_account_move_values())
            new_move.action_post()
            record.account_move_id = new_move.id
            new_move.update({'hr_expense_advance_related_id': record,
                             'check_advance': True,
                             'payment_state': 'not_paid',
                             'partner_id': record.employee_id.user_id.partner_id.id,
                             })
        return self.write({"state": "approved"})

    def action_register_payment(self):
        not_approved_advances = self.filtered(lambda a: a.state != 'approved')
        non_scheduled_advances = self.filtered(lambda a: not a.scheduled_payment_day or not a.payment_journal_id)
        early_scheduled_advances = self.filtered(
            lambda a: a.scheduled_payment_day and a.scheduled_payment_day > fields.Date.today())
        not_manager_approved_advances = self.filtered(lambda a: not a.approved_manager)

        if not_approved_advances:
            raise ValidationError(
                _(f"The following Advances are not in approved state:\n{not_approved_advances.mapped('name')}"))

        if non_scheduled_advances:
            raise ValidationError(
                _(f"The following Advances does not have all the payment schedule info:\n{non_scheduled_advances.mapped('name')}"))

        if early_scheduled_advances:
            raise ValidationError(
                _(f"The following Advances have a payment date after today's date:\n{early_scheduled_advances.mapped('name')}"))

        if not_manager_approved_advances:
            raise ValidationError(
                _(f"The following Advances payments are not approved by manager:\n{not_manager_approved_advances.mapped('name')}"))

        if len(self.mapped('payment_journal_id')) > 1:
            raise ValidationError(
                _(f"There are documents with different payment bank configured, please all records should have the same bank"))

        draft_account_moves = self.mapped('account_move_id').filtered(lambda m: m.state == 'draft')
        draft_account_moves.action_post()

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.mapped('account_move_id').ids,
                'default_partner_bank_id': self.employee_id.sudo().bank_account_id.id,
                'default_journal_id': self.mapped('payment_journal_id')[0].id,
                'default_from_expense_advance': True,
                'expense_advances_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def button_reject(self):
        return self.write({"state": "refused"})

    def compute_activity_approved_to_paid(self):
        for rec in self:
            #  Marca actividad como hecha de forma automatica
            new_activity = rec.env['mail.activity'].search([('id', '=', rec.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es Aprobado')
