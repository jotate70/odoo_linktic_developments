from odoo import models, _, fields


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    payment_id = fields.Many2one(comodel_name='account.payment', string='Payment Generated', default=False)

    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'payroll.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.env.context.get('active_ids')},
            'type': 'ir.actions.act_window',
        }