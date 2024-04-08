from odoo import models, _, fields


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    payment_ids = fields.One2many(comodel_name='account.payment', inverse_name='payslip_run_id')
    payment_count = fields.Integer(compute='_compute_payment_count', string="Payment Count")
    payslip_count = fields.Integer(compute='_compute_payslip_count', string="Payslip Count")

    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    def _compute_payslip_count(self):
        for record in self:
            record.payslip_count = len(self.slip_ids.filtered(lambda s: s.state == 'done'))

    def payment_preview(self):
        return {
            'name': _('Payslip Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', self.payment_ids.ids)],
        }

    def payslip_preview(self):
        return {
            'name': _("Payslip's"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', self.slip_ids.filtered(lambda s: s.state == 'done').ids)],
        }
