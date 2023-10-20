from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from datetime import date

class ContractorChargeAccount(models.Model):
    _name = 'hr.contractor.charge.account'
    _description = "Contractor Charge Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_contractor_default_journal(self):
        return self.env["account.journal"].browse(self.env.company.contractor_charge_default_journal.id)

    name = fields.Char(string='Charge Account', default=lambda self: _("New"))
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    employee_id = fields.Many2one("hr.employee", string="Employee", ondelete="restrict")
    contract_id = fields.Many2one("hr.contract", string="Contract", ondelete="restrict",
                                  domain="[('employee_id', '=?', employee_id)]")
    journal_ids = fields.Many2many(comodel_name='account.journal', string='Account Journals',
                                   check_company=True,
                                   related='company_id.contractor_charge_default_journal_ids')
    journal_id = fields.Many2one('account.journal', string='Charge Account Journal',
                                 # states={'done': [('readonly', True)], 'post': [('readonly', True)]},
                                 check_company=True,
                                 domain="[('id', '=', journal_ids)]",
                                 # domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
                                 default=_get_contractor_default_journal,
                                 help="The journal used when the Charge Account is done.")
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('budget_approval', 'Budget Approval'),
                   ('approved', 'Approved'), ('rejected', 'Rejected')]
        , string="Status", index=True, tracking=True, required=True, copy=False, default="draft")
    line_ids = fields.One2many(comodel_name="hr.contractor.charge.account.line",
                               inverse_name="contractor_charge_account_id",
                               string="Participation Information")
    charge_account_attachment = fields.Binary(string="Charge Account Attachment")
    charge_account_att_name = fields.Char(string="Charge Account Attachment Name")
    parafiscal_attachment = fields.Binary(string="Parafiscal Attachment")
    parafiscal_att_name = fields.Char(string="Parafiscal Attachment Name")
    rut_attachment = fields.Binary(string="RUT Attachment")
    rut_att_name = fields.Char(string="RUT Attachment Name")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    total_amount = fields.Float(string='Total')
    notes = fields.Text(string='Observations')
    invoice_ids = fields.One2many(comodel_name="account.move",
                                  inverse_name="hr_contractor_charge_account_id",
                                  string="Bills")
    invoice_count = fields.Integer(compute="_compute_invoice_count", string='Bill Count', default=0)
    invoice_state = fields.Char(string='Bill State', compute='get_invoice_state_label')
    is_my_contractor_charges = fields.Boolean(string='is_my_charges')

    def _compute_demo(self):
        self.write({'journal_domain': self.journal_ids.ids})

    @api.model
    def default_get(self, fields_list):
        res = super(ContractorChargeAccount, self).default_get(fields_list)
        if self._context.get('default_is_my_contractor_charges'):
            employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
            res.update({'employee_id': employee_ids.ids[0]})
        return res

    def get_invoice_state_label(self):
        for record in self:
            if record.invoice_ids:
                # record.invoice_state = record.invoice_ids[0].state
                record.invoice_state = dict(record.invoice_ids[0]._fields['state'].selection).get(
                    record.invoice_ids[0].state)
            else:
                record.invoice_state = False

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("hr.contractor.charge.account")
        return super(ContractorChargeAccount, self).create(vals)

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    @api.constrains('contract_id', 'date_start', 'date_end')
    def _check_line_date(self):
        for record in self:
            domains = [[('date_start', '<', record.date_end), ('date_end', '>=', record.date_start),
                        ('contract_id', '=', record.contract_id.id), ('state', '!=', 'rejected')]]
            domain = expression.OR(domains)

            charge_account_in_range = self.search(domain)
            if len(charge_account_in_range) > 1:
                raise ValidationError(_("This date range overlaps with another charge account for this contract."))

            # Check that the date range of the charge is in range of the selected contract
            contract_end_date = record.contract_id.date_end or date(2999, 12, 31)
            if record.date_start < record.contract_id.date_start or record.date_end > contract_end_date:
                raise ValidationError(
                    _("The contract %s has a date range of (%s to %s), the dates of the charge account cannot be outside this date range.") % (
                        record.contract_id.name, record.contract_id.date_start.strftime("%d-%m-%Y"),
                        record.contract_id.date_end.strftime("%d-%m-%Y") if record.contract_id.date_end else _(
                            "Undefined")))

    def populate_line_hours(self):
        self.ensure_one()

        reported_hours = self.env['hr.contractor.reported.hours'].search(
            [('employee_identification', '=', self.employee_id.sudo().identification_id),
             ('date', '>=', self.date_start), ('date', '<=', self.date_end), ('company_id', '=', self.company_id.id)])
        line_val_list = []

        for analytic_account in list(set(reported_hours.mapped('account_analytic_code'))):
            analytic_account_obj = self.env['account.analytic.account'].search([('code', '=', analytic_account)])
            hours_value = sum(
                reported_hours.filtered(lambda r: r.account_analytic_code == analytic_account).mapped('hours'))

            budget_lines = self.env['crossovered.budget.lines'].search(
                [('analytic_account_id', '=', analytic_account_obj.id),
                 ('general_budget_id.is_payroll_position', '=', True), ('date_from', '<=', self.date_start),
                 ('date_to', '>=', self.date_end)])

            budget_responsible = budget_lines.mapped('crossovered_budget_id').user_id

            if analytic_account_obj:
                line_val = {
                    # 'contractor_charge_account_id': self.id,
                    'account_analytic_id': analytic_account_obj.id,
                    'reported_hours': hours_value,
                    'responsible_id': budget_responsible.id,
                }
                # new_line = self.env['hr.contractor.charge.account.line'].new(line_val)
                line_val_list.append((0, 0, line_val))

        self.line_ids = [(2, line) for line in self.line_ids.ids]
        self.line_ids = line_val_list

        for line in self.line_ids:
            if self.contract_id.payment_period == 'hour':
                line.line_total = line.reported_hours * self.contract_id.total_income
            elif self.contract_id.payment_period == 'month':
                total_hours = sum(self.line_ids.mapped('reported_hours'))
                # worked_days = relativedelta(self.date_end, self.date_start).days
                worked_days = len(set(reported_hours.mapped('date')))
                month_days = monthrange(self.date_start.year, self.date_start.month)
                line_percentage = line.reported_hours / total_hours
                line.line_total = line_percentage * self.contract_id.total_income / month_days[1] * worked_days

        self.total_amount = sum(self.line_ids.mapped('line_total'))

    def button_request_approval(self):
        for record in self:
            if not record.charge_account_attachment or not record.parafiscal_attachment or not record.rut_attachment:
                raise ValidationError(_("Cannot send to approve a charge account without attachments set."))

            if not record.line_ids:
                raise ValidationError(_("Cannot send to approve a charge account without reported hours"))

            if any(not line.responsible_id for line in self.line_ids):
                raise ValidationError(_("Cannot send to approve a charge account with no responsible assigned lines"))

            record.line_ids.state = 'to_approve'
            record.update({'state': 'to_approve'})

        #   ////////////////// New Code /////////////////////////////
            if self.state == 'to_approve':
                self._auto_to_approve_notification_email()

    def button_budget_approval(self):
        for record in self:
            if not record.charge_account_attachment or not record.parafiscal_attachment or not record.rut_attachment:
                raise ValidationError(_("Cannot send to approve a charge account without attachments set."))

            record.create_contractor_bill()
            record.update({'state': 'approved'})

    def button_cancel(self):
        for record in self:
            record.update({'state': 'rejected'})

    def button_cancel2(self):
        for record in self:
            record.update({'state': 'rejected'})
            record.line_ids.state = 'rejected'

    def create_contractor_bill(self):
        for record in self:
            line_list = []
            for line in record.line_ids:
                line_list.append((0, 0, line._prepare_account_move_line()))

            bill_header_values = {
                'hr_contractor_charge_account_id': self.id,
                'partner_id': self.employee_id.sudo().address_home_id.id,
                'invoice_date': fields.Date.today(),
                'date': fields.Date.today(),
                'move_type': 'in_invoice',
                'journal_id': self.journal_id.id,
                'invoice_line_ids': line_list
            }

            self.env['account.move'].create(bill_header_values)

    def open_charge_account_bill(self):
        invoices = self.invoice_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    # //////////////////////// New Code ////////////////////////////////////////////
    def _auto_to_approve_notification_email(self):
        # Create Activity
        if self.line_ids:
            for rec in self.line_ids:
                user_approval = rec.responsible_id
                if not user_approval:
                    raise ValidationError("There is no default budget approver, please set it up in settings menu.")
                shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
                self.env['mail.activity'].create({
                    'summary': _('Contractor Charge Account Budget Approval'),
                    'date_deadline': fields.Date.today() + relativedelta(days=shift),
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'res_model_id': self.env.ref("linktic_contractor_charge_account.model_hr_contractor_charge_account").id,
                    'res_id': self.id,
                    'user_id': user_approval.id,
                    'note': _("Por favor %s revisar la información de la cuenta de cobro %s la cual necesita una aprobación de presupuesto.") % (user_approval.name, self.name),
                })

    def _action_to_confirm_activity(self, responsible_id):
        #  Mark activity as done automatically
        if self.activity_ids:
            new_activity = self.env['mail.activity'].search([('id', 'in', self.activity_ids.ids), ('user_id', '=', responsible_id.ids)], limit=1)
            new_activity.action_feedback(feedback='Es Aprobado')

class ContractorChargeAccountLine(models.Model):
    _name = 'hr.contractor.charge.account.line'
    _description = "Contractor Charge Account Line"

    name = fields.Char(string='Description')
    contractor_charge_account_id = fields.Many2one('hr.contractor.charge.account', string='Charge Account',
                                                   required=True)
    header_state = fields.Selection(string="Charge Account State",
                                    selection=[('draft', 'Draft'), ('to_approve', 'To Approve'),
                                               ('budget_approval', 'Budget Approval'),
                                               ('approved', 'Approved'), ('rejected', 'Rejected')]
                                    , related="contractor_charge_account_id.state")
    contractor_charge_account_employee_id = fields.Many2one("hr.employee",
                                                            related='contractor_charge_account_id.employee_id')
    state = fields.Selection(selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'),
                                        ('rejected', 'Rejected')]
                             , string="Status", index=True, tracking=True, required=True, copy=False, default="draft")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    reported_hours = fields.Integer(string='Reported Hours')
    line_total = fields.Float(string='Value')
    responsible_id = fields.Many2one('res.users', string='Responsible', index=True)
    approval_date = fields.Date(string="Approval Date")
    is_line_approver = fields.Boolean(compute="get_approval_users")

    def get_approval_users(self):
        for record in self:
            if self.env.user == record.responsible_id:
                record.is_line_approver = True
            else:
                record.is_line_approver = False

    @api.onchange('state')
    def set_approval_date(self):
        if self.state in ('approved', 'rejected'):
            self.approval_date = fields.Date.today()
            #   New Code
            self.contractor_charge_account_id._action_to_confirm_activity(self.responsible_id)
        else:
            self.approval_date = False

    @api.constrains('state')
    def auto_approve_reject_charge(self):
        for record in self:
            if record.state == 'rejected':
                record.contractor_charge_account_id.state = 'rejected'
            if record.state == 'approved':
                if all(line.state == 'approved' for line in record.contractor_charge_account_id.line_ids):
                    record.contractor_charge_account_id.state = 'budget_approval'

                    # Create Activity
                    user_approval = self.contractor_charge_account_id.company_id.contactor_budget_approver
                    if not user_approval:
                        raise ValidationError(
                            _("There is no default budget approver, please set it up in settings menu."))

                    shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
                    self.env['mail.activity'].create({
                        'summary': _('Contractor Charge Account Budget Approval'),
                        'date_deadline': fields.Date.today() + relativedelta(days=shift),
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'res_model_id': self.env.ref(
                            "linktic_contractor_charge_account.model_hr_contractor_charge_account").id,
                        'res_id': self.contractor_charge_account_id.id,
                        'user_id': user_approval.id,
                        'note': _(
                            "Please %s review the information of the contractor charge account %s which needs a budget approval.") % (
                                    user_approval.name, self.name),
                    })


    def _prepare_account_move_line(self):
        self.ensure_one()
        employee = self.env['hr.employee.public'].sudo().browse(self.contractor_charge_account_id.employee_id.id)
        return {
            'name': '%s: %s, %s' % (self.contractor_charge_account_id.name,
                                    self.contractor_charge_account_id.company_id.contractor_charge_product_id.name,
                                    employee.sudo().job_id.name),
            'product_id': self.contractor_charge_account_id.company_id.contractor_charge_product_id.id,
            'product_uom_id': self.contractor_charge_account_id.company_id.contractor_charge_product_id.uom_po_id.id,
            'quantity': 1,
            'price_unit': self.line_total,
            'analytic_account_id': self.account_analytic_id.id,
        }
