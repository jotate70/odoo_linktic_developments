from odoo import models, fields, _
from odoo.exceptions import UserError


class PayrollPayment(models.TransientModel):
    _name = 'payroll.payment'
    _description = 'Payroll Payment'

    company_id = fields.Many2one(comodel_name='res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Charge Account Journal',
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
                                 required=True)
    payment_date = fields.Date(string="Payment Date", default=fields.Datetime.now, required=True)

    def action_create_payments(self):
        payslip_ids = self.env['hr.payslip'].browse(self.env.context.get('active_ids'))

        not_bank_partners = payslip_ids.mapped('employee_id.address_home_id').filtered(lambda p: not p.bank_ids)
        if not_bank_partners:
            error = (_("These employees do not have a bank account set up:\n"))
            for partner in not_bank_partners:
                error += f"- {partner.name}\n"
            raise UserError(error)

        payment_payslips = payslip_ids.filtered(lambda p: p.payment_id)
        if payment_payslips:
            error = (_("It is not possible to create payments for the following payrolls, since they have a payment associated with them:\n"))
            for payslip in payment_payslips:
                error += f"- {payslip.number + _(' for the employee ') + payslip.employee_id.name}\n"
            raise UserError(error)

        payments = []
        payment_date = self.payment_date
        journal_id = self.journal_id
        currency_id = self.env.company.currency_id
        payment_method_line_id = self.env['account.payment.method.line'].search([('journal_id', '=', journal_id.id), ('payment_type', '=', 'outbound')])

        for payslip in payslip_ids:

            line = payslip.move_id.line_ids.filtered(lambda l: l.partner_id == payslip.employee_id.address_home_id and l.credit > 0 and l.account_id.group_payslip)
            partner_id = payslip.employee_id.address_home_id

            payment_vals = {
                'amount': line.credit,
                'ref': payslip.name,
                'partner_id': partner_id.id,
                'destination_account_id': line.account_id.id,
                'partner_bank_id': partner_id.bank_ids[0].id,
                'payment_method_line_id': payment_method_line_id.id,
                'currency_id': currency_id.id,
                'date': payment_date,
                'journal_id': journal_id.id,
                'payment_type': 'outbound',
            }

            payment_id = self.env['account.payment'].create(payment_vals)
            payment_id.action_post()
            payments.append(payment_id.id)
            payslip.write({
                'payment_id': payment_id.id
            })
            payslip.payslip_run_id.write({
                'payment_ids': [(6, 0, payments)]
            })

        return {
            'name': _('Payslip Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', payments)],
        }
