from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # _public_required_attachments = ['att_technical_proposal', 'att_specification', 'att_attachment',
    #                                 'att_adjudication_certificate', 'att_contract', 'att_policy', 'att_business_case']
    # _commercial_required_attachments = ['att_technical_proposal', 'att_approval_mail', 'att_contract',
    #                                     'att_policy', 'att_business_case']

    sale_type = fields.Selection(selection=[('public', 'Public Tender'), ('commercial', 'Commercial Management')],
                                 required=True)
    att_technical_proposal = fields.Binary(string="Technical Proposal")
    att_technical_proposal_name = fields.Char(string="Contract Attachment Name")
    att_specification = fields.Binary(string="Specification")
    att_specification_name = fields.Char(string="Specification Name")
    att_attachment = fields.Binary(string="Attachments")
    att_attachment_name = fields.Char(string="Attachments Name")
    att_adjudication_certificate = fields.Binary(string="Adjudication Certificate")
    att_adjudication_certificate_name = fields.Char(string="Adjudication Certificate Name")
    att_contract = fields.Binary(string="Contract")
    att_contract_name = fields.Char(string="Contract Name")
    att_policy = fields.Binary(string="Policy")
    att_policy_name = fields.Char(string="Policy Name")
    att_business_case = fields.Binary(string="Business Case")
    att_business_case_name = fields.Char(string="Business Case Name")
    att_approval_mail = fields.Binary(string="Approval Mail/Purchase Order")
    att_approval_mail_name = fields.Char(string="Approval Mail Name")
    can_create_invoice = fields.Boolean('can create invoice')
    crm_team_goal_id = fields.Many2one('crm.team.goal', compute='get_sale_team_goal')
    policy_purchase_order_id = fields.Many2one('purchase.order', string="Policy Purchase Order",
                                               domain=[('mandatory_policy', '=', False), ('need_policy', '=', True),
                                                       ('project_id', '=', False)])

    def get_sale_team_goal(self):
        for sale in self:
            sales_domain = [('date_start', '<=', sale.date_order), ('date_end', '>=', sale.date_order),
                            ('team_id', '=', sale.team_id.id)]
            sale.crm_team_goal_id = self.env['crm.team.goal'].search(sales_domain).id

    def action_confirm(self):
        """Assign the project created to the PO project and purchase Request if exists"""
        """Create a new Budget with a INITIAL BUDGET position by default"""
        result = super(SaleOrder, self).action_confirm()
        for so in self:
            if so.policy_purchase_order_id:
                so.policy_purchase_order_id.project_id = so.project_ids[0]

                purchase_quotation = self.env['purchase.request.quotation'].search(
                    [('purchase_order_id', '=', so.policy_purchase_order_id.id)])
                if purchase_quotation:
                    purchase_quotation.purchase_request_line_id.request_id.project_id = so.project_ids[0]

            # Create the new Budget with a default budgetary position
            new_budget = so.create_default_budget()

        return result

    def action_assign_purchase_policy(self):
        """ Returns an action opening the assign policy wizard"""
        new_wizard = self.env['sale.order.assign.policy.wizard'].with_context(active_asset=self).create({
            'sale_order_id': self.id})
        return {
            'name': _('Assign Policy Purchase'),
            'view_mode': 'form',
            'res_model': 'sale.order.assign.policy.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def create_default_budget(self):
        self.ensure_one()

        # Segregation Values
        segregation_vals = {
            'name': _('Initial Budget'),
            'quantity': 1,
            'planned_amount': -5000000,
        }

        # crossovered_budget_line Vals
        line_vals = {
            'general_budget_id': self.env.ref('linktic_sales.initial_budget_post').id,
            'analytic_account_id': self.analytic_account_id.id,
            'date_from': self.date_order,
            'date_to': date(self.date_order.year, 12, 31),
            'budget_line_segregation_id': [(0, 0, segregation_vals)]
        }

        # Header Values
        header_vals = {
            'name': self.analytic_account_id.display_name,
            'date_from': self.date_order,
            'date_to': date(self.date_order.year, 12, 31),
            'analytic_account_id': self.analytic_account_id.id,
            'user_id': self.user_id.id,
            'crossovered_budget_line': [(0, 0, line_vals)]
        }

        return self.env['crossovered.budget'].create(header_vals)
