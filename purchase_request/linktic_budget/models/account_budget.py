from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    project_id = fields.Many2one('project.project', 'Project', compute="_get_budget_project")

    def _get_budget_project(self):
        for budget in self:
            if budget.analytic_account_id:
                budget.project_id = self.env['project.project'].search(
                    [('analytic_account_id', '=', budget.analytic_account_id.id)])
            else:
                budget.project_id = False

    @api.constrains('analytic_account_id')
    def _unique_budget_project(self):
        for record in self:
            if record.analytic_account_id:
                projects_with_ana = self.env['project.project'].search(
                    [('analytic_account_id', '=', record.analytic_account_id.id)])
                budgets_with_ana = self.env['crossovered.budget'].search(
                    [('analytic_account_id', '=', record.analytic_account_id.id), ('id', '!=', record.id)])
                if projects_with_ana and budgets_with_ana:
                    raise ValidationError(
                        _("Cannot use this Analitycal Account, because is already used in another budget"))

    @api.onchange('analytic_account_id')
    def _update_analytic_budget_lines(self):
        if self.analytic_account_id:
            for b_line in self.crossovered_budget_line:
                b_line.analytic_account_id = self.analytic_account_id


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    planned_amount = fields.Monetary(required=False, compute='_compute_planned_amount', store=True)
    budget_line_segregation_id = fields.One2many('crossovered.budget.lines.segregation', 'crossovered_budget_line_id',
                                                 'Budget Line Segregation', copy=False)

    def action_open_budget_line_segregation(self):
        if self.general_budget_id.is_payroll_position:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'linktic_budget.crossovered_budget_lines_segregation_payroll_action')
        else:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'linktic_budget.crossovered_budget_lines_segregation_action')
        action['domain'] = [('crossovered_budget_line_id', '=', self.id)]
        action['context'] = {'default_crossovered_budget_line_id': self.id}
        return action

    @api.depends('budget_line_segregation_id.planned_amount')
    def _compute_planned_amount(self):
        for line in self:
            line.planned_amount = sum(line.budget_line_segregation_id.mapped('planned_amount'))


class CrossoveredBudgetLinesSegregation(models.Model):
    _name = "crossovered.budget.lines.segregation"
    _description = "Budget Line Segregation"

    name = fields.Char(string="Description", required=True)
    crossovered_budget_line_id = fields.Many2one('crossovered.budget.lines', 'Budget Line', ondelete='cascade',
                                                 index=True, required=True)
    quantity = fields.Integer(string="Quantity", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          related='crossovered_budget_line_id.analytic_account_id')
    analytic_group_id = fields.Many2one('account.analytic.group', 'Analytic Group',
                                        related='analytic_account_id.group_id', readonly=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position',
                                        related='crossovered_budget_line_id.general_budget_id')
    date_from = fields.Date('Start Date', related='crossovered_budget_line_id.date_from')
    date_to = fields.Date('End Date', related='crossovered_budget_line_id.date_to')
    paid_date = fields.Date('Paid Date', related='crossovered_budget_line_id.paid_date')
    currency_id = fields.Many2one('res.currency', related='crossovered_budget_line_id.currency_id', readonly=True)
    planned_amount = fields.Monetary(
        'Planned Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Practical Amount', help="Amount really earned/spent.")
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount', string='Theoretical Amount',
        help="Amount you are supposed to have earned/spent at this date.")
    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    company_id = fields.Many2one(related='crossovered_budget_line_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    crossovered_budget_state = fields.Selection(related='crossovered_budget_line_id.crossovered_budget_state'
                                                , string='Budget State', store=True, readonly=True)
    job_position_id = fields.Many2one('hr.job', string="Job Position",
                                      help="Only used when the budgetary position is payroll")
    salary_scale_id = fields.Many2one('hr.job.salary.scale', string="Seniority",
                                      domain="[('job_id', '=', job_position_id)]")
    position_months = fields.Integer('Months')
    occupation_perc = fields.Float(string="Occupation %")

    @api.onchange('job_position_id', 'position_months', 'quantity', 'occupation_perc', 'salary_scale_id')
    def update_segregation_info(self):
        for record in self:
            if record.job_position_id:
                if record.salary_scale_id:
                    record.name = record.job_position_id.name + " - " + record.salary_scale_id.name
                    record.planned_amount = record.salary_scale_id.avg_job_salary * record.position_months * record.quantity * record.occupation_perc
                else:
                    record.name = record.job_position_id.name
                    record.planned_amount = 0

    def _is_above_budget(self):
        for line in self:
            if line.theoritical_amount >= 0:
                line.is_above_budget = line.practical_amount > line.theoritical_amount
            else:
                line.is_above_budget = line.practical_amount < line.theoritical_amount

    def _compute_practical_amount(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('budget_line_segregation_id', '=', line.id),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('budget_line_segregation_id', '=', line.id),
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount = self.env.cr.fetchone()[0] or 0.0

    def _compute_theoritical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if line.paid_date:
                if today <= line.paid_date:
                    theo_amt = 0.00
                else:
                    theo_amt = line.planned_amount
            else:
                line_timedelta = line.date_to - line.date_from
                elapsed_timedelta = today - line.date_from

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and today < line.date_to:
                    # If today is between the budget line date_from and date_to
                    theo_amt = (
                                       elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                else:
                    theo_amt = line.planned_amount
            line.theoritical_amount = theo_amt

    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount)
            else:
                line.percentage = 0.00

    @api.constrains('general_budget_id', 'analytic_account_id')
    def _must_have_analytical_or_budgetary_or_both(self):
        if not self.analytic_account_id and not self.general_budget_id:
            raise ValidationError(
                _("You have to enter at least a budgetary position or analytic account on a budget line."))

    def action_open_budget_entries(self):
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
            action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to)
                                ]
            if self.general_budget_id:
                action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
        else:
            # otherwise the journal entries booked on the accounts of the budgetary postition are opened
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
            action['domain'] = [('account_id', 'in',
                                 self.general_budget_id.account_ids.ids),
                                ('date', '>=', self.date_from),
                                ('date', '<=', self.date_to)
                                ]
        return action


class AccountBudgetPost(models.Model):
    _inherit = "account.budget.post"

    name = fields.Char(translate=True)
    is_payroll_position = fields.Boolean(string="Is a Payroll Position", default=False)
    is_policy_position = fields.Boolean(string="Is a Policy Position", default=False)
    company_id = fields.Many2one(required=False)

    @api.constrains('is_policy_position')
    def _unique_policy_position(self):
        for record in self:
            if record.is_policy_position:
                created_policy_position = self.env['account.budget.post'].search(
                    [('id', '!=', record.id if isinstance(record.id, int) else record.id.origin),
                     ('is_policy_position', '=', True)])

                if created_policy_position:
                    raise ValidationError(
                        _("Only 1 Budgetary position can be active for all companies, please uncheck this option in the position (%s)." % (
                            created_policy_position.name)))

                if record.company_id:
                    raise ValidationError(_("The policy budgetary position has to have an empty company value"))

    @api.onchange('is_policy_position')
    def _onchange_policy_position(self):
        if self.is_policy_position:
            self.company_id = False
            self._unique_policy_position()
