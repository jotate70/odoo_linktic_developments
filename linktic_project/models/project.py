from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from .project_update import STATUS_COLOR
from datetime import timedelta, datetime


class ProjectProject(models.Model):
    _inherit = "project.project"

    percentage_done = fields.Float("Percentage Done", compute="_get_sum_subtask_percentage")
    sponsor = fields.Many2one('res.users', string='Sponsor', tracking=True)
    project_size = fields.Many2one('project.size', string='Size', tracking=True)
    methodology_id = fields.Many2one('project.methodology', string="Methodology", tracking=True)
    contract_start_date = fields.Date(string="Contract Start Date")
    contract_end_date = fields.Date(string="Contract End Date")
    project_duration = fields.Integer(string="Project Duration", compute="_get_project_duration")
    project_type = fields.Selection(selection=[('external', 'External'), ('internal', 'Internal')], string="Type")
    sector = fields.Selection(selection=[('public', 'Public'), ('private', 'Private')], string="Sector")
    project_object = fields.Html(string="Object")
    scope = fields.Html(string="Scope")
    document_repository = fields.Char(string="Documents Repository")
    last_update_status = fields.Selection(selection_add=[
        ('suspended', 'Suspended'),
        ('canceled', 'Canceled'),
        ('lapsed', 'Lapsed'),
        ('on_sale', 'On Sale'),
        ('sold', 'Sold Out'),
        ('support', 'Support'),
    ])
    policy_order_ids = fields.One2many('purchase.order', 'project_id', string='Policy Orders', copy=False)
    policy_count = fields.Integer(string='Policy Count', compute="get_policy_count")

    @api.depends('last_update_status')
    def _compute_last_update_color(self):
        for project in self:
            project.last_update_color = STATUS_COLOR.get(project.last_update_status)
            if not project.last_update_color:
                super(ProjectProject, project)._compute_last_update_color()

    def _get_sum_subtask_percentage(self):
        for record in self:
            first_lvl_task = record.tasks.filtered(lambda t: not t.parent_id)
            if first_lvl_task:
                record.percentage_done = round(sum(first_lvl_task.mapped('parent_task_percentage')) * 100, 2)
            else:
                record.percentage_done = 0.0

    def _get_project_duration(self):
        for record in self:
            if record.contract_end_date and record.contract_start_date:
                record.project_duration = (record.contract_end_date - record.contract_start_date).days
            else:
                record.project_duration = False

    def generate_policy(self):
        self.ensure_one()

        action = self.env.ref('purchase_request.purchase_request_form_action')
        result = action.read()[0]

        purchase_request_upd = self.env['purchase.request'].search([('project_id', '=', self.id)])
        if not purchase_request_upd:
            raise ValidationError(_("This project does not have a purchase request with policies"))

        policy_prod_template = self.env['product.template'].search([('is_policy_product', '=', True)])

        new_purchase_line_dict = {
            'state': 'draft',
            'product_id': self.env['product.product'].search([('product_tmpl_id', '=', policy_prod_template.id)]).id,
            'product_qty': 1,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'analytic_account_id': self.analytic_account_id.id,
            'general_budget_id': self.env['account.budget.post'].search([('is_policy_position', '=', True)]).id,
        }
        purchase_request_upd.line_ids = [(0, 0, new_purchase_line_dict)]
        purchase_request_upd.state = 'draft'

        res = self.env.ref('purchase_request.view_purchase_request_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            result['views'] = form_view

        purchase_request_upd = self.env['purchase.request'].search([('project_id', '=', self.id)])
        result['res_id'] = purchase_request_upd.id
        return result

    @api.depends('policy_order_ids')    # New code
    def get_policy_count(self):
        for project in self:
            project.policy_count = len(project.policy_order_ids)

    def open_policies(self):
        return {
            'name': _('Policies'),
            'domain': [('order_id.project_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'purchase.order.line',
            'view_id': self.env.ref('purchase_request.policy_purchase_order_line_tree').id,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }


class ProjectTask(models.Model):
    _inherit = "project.task"

    percentage_value = fields.Float("Percentage Value",
                                    help="Percentage Value of the subtask on the direct Parent task")
    parent_task_percentage = fields.Float("Percentage on Parent Task", compute="_get_sum_timesheet_percentage")
    child_ids_count = fields.Integer("Subtask Count", compute="_get_count_child_timesheet_task")
    timesheet_ids_count = fields.Integer("Timesheet Count", compute="_get_count_child_timesheet_task")

    def _get_count_child_timesheet_task(self):
        for task in self:
            task.child_ids_count = len(task.child_ids)
            task.timesheet_ids_count = len(task.timesheet_ids)

    def _get_sum_timesheet_percentage(self):
        for task in self.with_context(active_test=False):
            task.parent_task_percentage = round(task.progress * task.percentage_value / 100, 2)

    def update_task_progress(self):
        """Recursive method that will compute the progress of current task and parent taxes that can be affected"""
        for task in self:
            if not task.child_ids:
                task.progress = round(sum(task.timesheet_ids.mapped('percentage_done') * 100), 2)
            else:
                task.progress = round(sum(task.child_ids.mapped('parent_task_percentage') * 100), 2)
            if task.parent_id:
                task.parent_id.update_task_progress()

    @api.constrains('percentage_value')
    def _check_parent_task_total_percentage(self):
        for record in self:
            if record.percentage_value > 0:
                if record.parent_id:
                    r_child_ids = record.parent_id.child_ids
                else:
                    r_child_ids = record.project_id.tasks.filtered(lambda t: not t.parent_id)
                if sum(r_child_ids.mapped('percentage_value')) > 1:
                    raise ValidationError(
                        _("The summation of all subtask percentage cannot be more than 100%"))

    @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours',  # 'child_ids.percentage_value',
                 'child_ids.parent_task_percentage')
    def _compute_progress_hours(self):
        # Override to compute when there is no planned hours but there is percentage in child tasks
        for task in self:
            if task.planned_hours > 0.0:
                task_total_hours = task.effective_hours + task.subtask_effective_hours
                task.overtime = max(task_total_hours - task.planned_hours, 0)
                if task_total_hours > task.planned_hours:
                    task.progress = 100
                else:
                    task.progress = round(100.0 * task_total_hours / task.planned_hours, 2)
            else:
                if not task.child_ids:
                    task.progress = round(sum(task.timesheet_ids.mapped('percentage_done')) * 100, 2)
                else:
                    task.progress = round(sum(task.child_ids.mapped('parent_task_percentage')) * 100, 2)

                task.overtime = 0


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    percentage_done = fields.Float("Percentage Done", default=0)

    @api.constrains('percentage_done')
    def _check_task_total_percentage(self):
        for record in self:
            if record.percentage_done > 0:
                if sum(record.task_id.timesheet_ids.mapped('percentage_done')) > 1:
                    raise ValidationError(
                        _("The summation of all advances for this task percentages cannot be more than 100%"))

                record.task_id.update_task_progress()


class ProjectSize(models.Model):
    _name = "project.size"
    _description = "Project Size Categorization"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Text("Description")


class ProjectMethodology(models.Model):
    _name = "project.methodology"
    _description = "Project Methodology Categorization"

    name = fields.Char("Name", index=True, required=True, tracking=True, translate=True)
    description = fields.Text("Description")
