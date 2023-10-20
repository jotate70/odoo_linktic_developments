# -*- coding: utf-8 -*-

from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    related_company_journal_id = fields.Many2one('account.journal', string='Related Company Payment Bank',
                                                 domain="[('company_id', '=', journal_related_company), ('type', 'in', ('bank', 'cash')), ('related_company', '=', False)]")
    journal_related_company = fields.Many2one('res.company', related="journal_id.related_company")

    def action_create_payments(self):
        for payment in self:
            if payment.journal_related_company:
                # Check if the source lean company has a journal with a related company configured with the active company
                other_company_journal = self.env['account.journal'].sudo().search(
                    [('related_company', '=', payment.company_id.id)])
                if not other_company_journal:
                    raise ValidationError(
                        _(f"There is no journal in ({payment.journal_related_company.name}) that address to this company"))

                # Create Journal Entry in the source company where the amount moves from bank account to inter-company
                # designated account
                for line in payment.line_ids:
                    loan_move = self.env['account.move'].create(payment._prepare_inter_company_move(line))
                    loan_move.action_post()

        return super(AccountPaymentRegister, self).action_create_payments()

    @api.model
    def _prepare_inter_company_move(self, account_move_line_id):
        """ Returns a dictionary with the values of a journal entry that will be created in the source of the payment
        of the intercompany payment.
            :param account_move_line_id: payable line associated with the payment
        """
        self.ensure_one()
        bill = account_move_line_id.move_id
        move_ref = _(f"Inter Company payment for invoice {bill.name} from company {self.company_id.name}.")
        journal_id = self.related_company_journal_id
        other_company_journal = self.env['account.journal'].sudo().search(
            [('related_company', '=', self.company_id.id)])
        related_company_currency = self.journal_related_company.currency_id
        current_currency = self.company_id.currency_id
        prec = related_company_currency.decimal_places
        lines_list = []
        payment_value = self.amount if len(self.line_ids) == 1 else abs(account_move_line_id.balance)

        deb_line = {
            'name': move_ref,
            'account_id': other_company_journal.loan_exit_account_id.id,
            'credit': 0.0,
            'debit': payment_value,
            'currency_id': related_company_currency != current_currency and current_currency.id or False,
            'amount_currency': related_company_currency != current_currency and - 1.0 * payment_value or 0.0,
            'partner_id': self.company_id.partner_id.id,
        }
        lines_list.append((0, 0, deb_line))

        cred_line = {
            'name': move_ref,
            'account_id': journal_id.default_account_id.id,
            'debit': 0.0,
            'credit': payment_value,
            'currency_id': related_company_currency != current_currency and current_currency.id or False,
            'amount_currency': related_company_currency != current_currency and payment_value or 0.0,
            'partner_id': self.company_id.partner_id.id,
        }
        lines_list.append((0, 0, cred_line))

        move_vals = {
            'ref': move_ref,
            'date': fields.Date.today(),
            'journal_id': journal_id.id,
            'line_ids': lines_list,
            'name': '/',
            'move_type': 'entry',
            'currency_id': related_company_currency.id,
        }

        return move_vals
