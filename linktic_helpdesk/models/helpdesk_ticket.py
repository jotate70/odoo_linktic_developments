from odoo import fields, _, models, api
from datetime import datetime
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _get_default_user_id(self):
        team_id = self.env['helpdesk.ticket.team'].browse(self._context.get('default_team_id')) or self.team_id
        return team_id.alias_user_id.id

    category_activity_type = fields.Selection(related="category_id.activity_type")
    can_edit_user_id = fields.Boolean(string="Can Edit Assigned to", compute="_get_can_edit_user_id")
    user_id = fields.Many2one(default=_get_default_user_id, tracking=True)
    ticket_stage_log_ids = fields.One2many('helpdesk.ticket.stage.log', 'helpdesk_ticket_id', string='Stage Logs',
                                           copy=False)
    stage_sequence = fields.Integer(string='Stage Sequence', help="Sequence in which the ticket flow is in the moment",
                                    default=1)
    stage_approve = fields.Boolean(string='Stage Approved', default=False,
                                   help="Field that shows if the assigned person approve when it is defined")
    user_stage_approver = fields.Boolean(string='Stage Approver User', compute="_get_approval_info")
    stage_needs_approval = fields.Boolean(string='Stage Approved', compute="_get_approval_info")

    # HR Recruitment fields
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    job_title = fields.Char(string='Job')
    recruitment_degree_id = fields.Many2one('hr.recruitment.degree', string="Grade")
    career = fields.Char(string='Career')
    experience = fields.Text(string='Type and experience time - Specific skills')
    working_modality = fields.Selection(
        selection=[('mixed', 'Mixed'), ('in_person', 'In Person'), ('remote', 'Remote')]
        , string="Working Modality", tracking=True, copy=False)
    working_time = fields.Selection(
        selection=[('half', 'Half Time'), ('full', 'Full Time'), ('deliverables', 'Defined by deliverables')]
        , string="Working Time", tracking=True, copy=False)
    contract_type_id = fields.Many2one('hr.contract.type', "Contract Type")
    contract_duration = fields.Char(string='Contract Duration')
    budget_post_id = fields.Many2one('account.budget.post', 'Budgetary Position',
                                     domain="[('is_payroll_position', '=', True)]")
    budget_value = fields.Float(string='Budget Value')
    date_start = fields.Date(string="Start Date")
    has_profile = fields.Boolean(string="Has profile")
    profile_attachments = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_helpdesk_profile_rel"
                                           , column1="m2m_id", column2="attachment_id", string="Profile Attachments")
    recruitment_applicant_ids = fields.One2many('hr.applicant', 'helpdesk_ticket_id', string='Recruitment Applicants',
                                                copy=False)
    recruitment_applicant_count = fields.Integer(string='Applicants Count', compute="get_hr_applicants_count")
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    # HR Update Contract Fields

    employee_id = fields.Many2one('hr.employee', string='Employee')
    hr_contract_id = fields.Many2one('hr.contract', string='Contract')
    contract_job_id = fields.Many2one('hr.job', related='hr_contract_id.job_id')
    contract_type_id = fields.Many2one('hr.contract.type', related='hr_contract_id.contract_type_id')
    contract_date_start = fields.Date(string='Contract Start Date', related='hr_contract_id.date_start')
    contract_date_end = fields.Date(string='Contract End Date', related='hr_contract_id.date_end')
    contract_wage = fields.Monetary('Contract Wage', related='hr_contract_id.wage')
    contract_welfare_aid = fields.Monetary('Welfare Assistance', related='hr_contract_id.welfare_aid')
    contract_food_aid = fields.Monetary('Food Assistance', related='hr_contract_id.food_aid')
    contract_transport_aid = fields.Monetary('Transport Assistance', related='hr_contract_id.transport_aid')
    contract_bearing_aid = fields.Monetary('Bearing Assistance', related='hr_contract_id.bearing_aid')
    contract_total_income = fields.Monetary('Total Income', related='hr_contract_id.total_income')
    # New values fields
    updated_job = fields.Char(string='New Job Position')
    updated_contract_type_id = fields.Many2one('hr.contract.type', string="New Contract Type")
    updated_contract_date_end = fields.Date(string='New Contract End Date')
    contract_wage_rise = fields.Monetary('Contract Wage Rise')
    updated_contract_total_income = fields.Monetary('New Total Income', compute='get_updated_contract_total_income')
    contract_update_justification = fields.Text(string='Change Justification')
    contract_info_log_ids = fields.One2many('helpdesk.contract.info.log', 'helpdesk_ticket_id',
                                            string='Change Info History', copy=False)
    contract_info_log_count = fields.Integer(string='Contract Info Logs Count', compute="get_contract_info_logs_count")

    def get_contract_info_logs_count(self):
        for ticket in self:
            ticket.contract_info_log_count = len(ticket.contract_info_log_ids)

    @api.onchange("employee_id")
    def reset_contract_id(self):
        for ticket in self:
            ticket.hr_contract_id = False

    @api.onchange("hr_contract_id")
    def reset_update_info(self):
        for ticket in self:
            if not ticket.hr_contract_id:
                ticket.updated_job = False
                ticket.updated_contract_type_id = False
                ticket.updated_contract_date_end = False
                ticket.contract_wage_rise = False
                ticket.contract_update_justification = False

    @api.onchange("employee_id", "category_id")
    def update_ticket_name_description(self):
        for ticket in self:
            if ticket.category_id.activity_type == 'update_contract':
                str_val = _("Update Contract Info. %s") % (ticket.employee_id.name or '')
                ticket.name = str_val
                ticket.description = str_val

    @api.depends('contract_wage_rise')
    def get_updated_contract_total_income(self):
        for ticket in self:
            if ticket.contract_wage_rise > 0:
                ticket.updated_contract_total_income = ticket.contract_wage_rise + ticket.contract_total_income
            else:
                ticket.updated_contract_total_income = False

    def get_hr_applicants_count(self):
        for ticket in self:
            ticket.recruitment_applicant_count = len(ticket.recruitment_applicant_ids)

    def open_ticket_hr_applicants(self):
        return {
            'name': _('Recruitment Applicants'),
            'domain': [('helpdesk_ticket_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hr.applicant',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def create(self, vals):
        # Check if ticket category has an internal flow defined to set the initial Stage
        stage_cat_relation = self.env['helpdesk.stage.category.relation'].search(
            [('category_id', '=', vals.get('category_id'))], limit=1, order='sequence')
        if stage_cat_relation:
            vals['stage_id'] = stage_cat_relation.stage_id.id

        tickets = super(HelpdeskTicket, self).create(vals)
        # fix attachment ownership
        for ticket in tickets:
            if ticket.profile_attachments:
                ticket.profile_attachments.write({'res_model': self._name, 'res_id': ticket.id})

            # Create Initial Log Entry for each ticket
            vals_log = {'helpdesk_ticket_id': ticket.id, 'datetime_start': datetime.now(), 'user_id': self.env.user.id,
                        'current_log': True, 'stage_id': ticket.stage_id.id}
            self.env['helpdesk.ticket.stage.log'].create(vals_log)

        return tickets

    @api.model
    def default_get(self, fields_list):
        res = super(HelpdeskTicket, self).default_get(fields_list)
        res['partner_id'] = self.env.user.partner_id
        return res

    def _get_can_edit_user_id(self):
        for record in self:
            record.can_edit_user_id = self.env.user.has_group(
                'helpdesk_mgmt.group_helpdesk_user_team') and self.env.user in self.team_id.user_ids

    def _get_approval_info(self):
        for record in self:
            actual_stage_category_relation = self.env['helpdesk.stage.category.relation'].search(
                [('sequence', '=', record.stage_sequence), ('category_id', '=', record.category_id.id),
                 ('stage_id', '=', record.stage_id.id)])

            record.stage_needs_approval = actual_stage_category_relation.approver_user_ids
            record.user_stage_approver = self.env.user in actual_stage_category_relation.approver_user_ids

    @api.onchange('team_id')
    def update_ticket_user_id(self):
        for record in self:
            if record.team_id:
                record.user_id = record.team_id.alias_user_id
            else:
                record.user_id = False

    def open_stage_transition_wizard(self):
        """Creates a new wizard that will add a log with the results of the ticket stage, computes the valid stages
        for the next step in the process flow configured on helpdesk_stage_category_relation model"""
        actual_stage_category_relation = self.env['helpdesk.stage.category.relation'].search(
            [('sequence', '=', self.stage_sequence), ('category_id', '=', self.category_id.id),
             ('stage_id', '=', self.stage_id.id)])

        if actual_stage_category_relation.approver_user_ids and not self.stage_approve:
            raise ValidationError(_("Cannot End this stage without the needed approval"))

        stage_category_relations = self.env['helpdesk.stage.category.relation'].search(
            [('sequence', '=', self.stage_sequence + 1), ('category_id', '=', self.category_id.id)])

        new_wizard = self.env['hr_recruitment_requisition_stage_transition_wizard'].create({
            'helpdesk_ticket_id': self.id, 'stage_sequence': self.stage_sequence,
            'valid_ticket_stage_ids': [(6, 0, stage_category_relations.mapped('stage_id').ids)]
        })
        return {
            'name': _('Stage Transition'),
            'view_mode': 'form',
            'res_model': 'hr_recruitment_requisition_stage_transition_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def open_update_contract_info_wizard(self):
        new_wizard = self.env['helpdesk.update.contract.info.wizard'].create({
            'helpdesk_ticket_id': self.id, 'wizard_updated_job': self.updated_job,
            'wizard_updated_contract_type_id': self.updated_contract_type_id.id,
            'wizard_updated_contract_date_end': self.updated_contract_date_end,
            'wizard_contract_wage_rise': self.contract_wage_rise,
        })
        return {
            'name': _('Update Contract Info.'),
            'view_mode': 'form',
            'res_model': 'helpdesk.update.contract.info.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def button_approve_stage(self):
        for ticket in self:
            ticket.stage_approve = True
