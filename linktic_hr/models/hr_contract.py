from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from odoo.osv import expression


class HrContract(models.Model):
    _inherit = "hr.contract"

    total_income = fields.Monetary("Total Income", compute="_get_employee_total_inc")
    transport_aid = fields.Monetary('Transport Assistance', compute="get_employee_transport_aid")
    food_aid = fields.Monetary('Food Assistance')
    welfare_aid = fields.Monetary('Welfare Assistance')
    bearing_aid = fields.Monetary('Bearing Assistance')
    payment_period = fields.Selection([('month', 'Month'), ('hour', 'Hour')], string='Payment Period', default='month'
                                      , required=True, tracking=True)

    def get_employee_transport_aid(self):
        for record in self:
            smlv_obj = self.env.ref("linktic_hr.hr_payroll_parameter_SMLV")
            trans_obj = self.env.ref("linktic_hr.hr_payroll_parameter_transport_aid")
            date_to_compare = record.date_end or fields.Date.today()
            current_smlv = smlv_obj.line_ids.filtered(lambda p: p.date_start <= date_to_compare <= p.date_end)
            current_trans = trans_obj.line_ids.filtered(lambda p: p.date_start <= date_to_compare <= p.date_end)
            if record.wage <= (current_smlv.value * current_trans.no_smlv) and record.payment_period == 'month':
                record.transport_aid = current_trans.value
            else:
                record.transport_aid = 0

    def _get_employee_total_inc(self):
        for record in self:
            record.total_income = record.wage + record.transport_aid + record.food_aid + record.welfare_aid \
                                  + record.bearing_aid

    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        """ Two contracts in state [incoming | open | close] cannot overlap
        Override, this validation will not apply to contractor employee type """
        for contract in self.filtered(lambda c: (c.state not in ['draft',
                                                                 'cancel'] or c.state == 'draft' and c.kanban_state == 'done') and c.employee_id):
            domain = [
                ('id', '!=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                ('company_id', '=', contract.company_id.id),
                ('employee_id.employee_type', '!=', 'contractor'),
                '|',
                ('state', 'in', ['open', 'close']),
                '&',
                ('state', '=', 'draft'),
                ('kanban_state', '=', 'done')  # replaces incoming
            ]

            if not contract.date_end:
                start_domain = []
                end_domain = ['|', ('date_end', '>=', contract.date_start), ('date_end', '=', False)]
            else:
                start_domain = [('date_start', '<=', contract.date_end)]
                end_domain = ['|', ('date_end', '>', contract.date_start), ('date_end', '=', False)]

            domain = expression.AND([domain, start_domain, end_domain])
            if self.search_count(domain):
                raise ValidationError(
                    _(
                        'An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts).\n\nEmployee: %(employee_name)s',
                        employee_name=contract.employee_id.name
                    )
                )
