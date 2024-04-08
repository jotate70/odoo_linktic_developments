from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class Team(models.Model):
    _inherit = 'crm.team'

    team_goal_ids = fields.One2many('crm.team.goal', 'team_id', string="Sales Team Goals")
    team_goals_count = fields.Integer('Goals Count', compute='get_goals_count')
    user_can_edit_goals = fields.Boolean(string='User Can Edit', compute='validate_user_permissions')

    def action_view_team_goals(self):
        self.ensure_one()
        if self.user_can_edit_goals:
            dest_view_id = self.env.ref('linktic_sales.view_crm_team_goals_tree_edit_create')
        else:
            dest_view_id = self.env.ref('linktic_sales.view_crm_team_goals_tree')

        return {
            'name': _('Sales Team Goals'),
            'domain': [('team_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'crm.team.goal',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'view_id': dest_view_id.id
        }

    def get_goals_count(self):
        for team in self:
            team.team_goals_count = len(team.team_goal_ids)

    def validate_user_permissions(self):
        for record in self:
            record.user_can_edit_goals = self.env.is_admin() or self.env.user.has_group('sales_team.group_sale_manager')


class Team(models.Model):
    _name = 'crm.team.goal'
    _description = "crm team goals"
    _order = "date_start"

    name = fields.Char(string='Description')
    team_id = fields.Many2one('crm.team', string='Sales Team')
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    sale_goal_amount = fields.Float(string="Sale Goal Amount")
    period_sales = fields.Float(string='Period Sales', compute='get_team_period_sales', store="True")
    goal_perc = fields.Float(string='% Achieved', compute='get_team_period_sales')
    sale_order_ids = fields.One2many('sale.order', 'crm_team_goal_id')

    @api.constrains('date_start', 'date_end')
    def _check_line_date(self):
        for goal in self:
            domains = [[('date_start', '<', goal.date_end), ('date_end', '>=', goal.date_start),
                        ('team_id', '=', goal.team_id.id), ('id', '!=', goal.id)]]
            domain = expression.OR(domains)

            goals_in_range = self.search(domain)

            if goals_in_range:
                raise ValidationError(_("This Sale goals overlaps with another goal set for this team"))

    @api.depends('sale_goal_amount', 'sale_order_ids')
    def get_team_period_sales(self):
        for goal in self:
            sales_domain = [('date_order', '>=', goal.date_start), ('date_order', '<=', goal.date_end),
                            ('team_id', '=', goal.team_id.id), ('state', '=', 'sale')]
            sales = self.env['sale.order'].search(sales_domain)

            goal.period_sales = sum(sales.mapped('amount_untaxed'))

            goal.goal_perc = goal.period_sales / goal.sale_goal_amount if goal.sale_goal_amount else 0
