from odoo import fields, _, models, api
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_check = fields.Boolean(string='Payment Check', tracking=True)
    related_move_ids = fields.One2many(comodel_name='account.move', inverse_name='payment_id2',
                                       string='Invoice Related', copy=True)

    # ////////////////////////////////  New fields  ////////////////////////////////////////////////

    batch_payment_id = fields.Many2one(comodel_name='account.batch.payment', compute="_compute_batch_payment_id",
                                       ondelete='set null', store=True, readonly=False)
    amount_signed = fields.Monetary(currency_field='currency_id', compute='_compute_amount_signed')

    # ////////////////////////////////////////////////////////////////////////////////////////////////

    @api.constrains('payment_method_line_id')
    def _check_payment_method_line_id(self):
        return

    @api.depends('reconciled_bill_ids')
    def _compute_related_move_ids(self):
        for rec in self:
            rec.write({'related_move_ids': [(6, 0, rec.reconciled_bill_ids.ids)] if rec.reconciled_bill_ids else False})

    def _compute_stat_buttons_from_reconciliation(self):
        res = super(AccountPayment, self)._compute_stat_buttons_from_reconciliation()
        self.write({'related_move_ids': [(6, 0, self.reconciled_bill_ids.ids)] if self.reconciled_bill_ids else False})
        return res

    @api.depends('state')
    def _compute_batch_payment_id(self):
        for rec in self:
            rec.batch_payment_id = rec.state == 'posted' and rec.batch_payment_id or None

    @api.depends('payment_type', 'amount')
    def _compute_amount_signed(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                rec.amount_signed = -rec.amount
            else:
                rec.amount_signed = rec.amount

    @api.model
    def action_create_batch_payment(self):
        create_batch_payment = {
            'journal_id': self[0].journal_id.id,
            'payment_ids': [(4, payment.id, None) for payment in self],
            'payment_method_id': self[0].payment_method_id.id,
            'batch_type': self[0].payment_type,
        }
        batch_payment = self.env['account.batch.payment'].sudo().create(create_batch_payment)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.batch.payment",
            "views": [[False, "form"]],
            "res_id": batch_payment.id,
        }

    def action_open_batch_payment(self):
        self.ensure_one()
        return {
            'name': _("Batch Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.batch.payment',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.batch_payment_id.id,
        }
    # ////////////////////////////////////////////////////////////////////////////////////////////////

    @api.depends('journal_id', 'payment_type', 'payment_method_line_id')
    def _compute_outstanding_account_id(self):
        super(AccountPayment, self)._compute_outstanding_account_id()

        for pay in self:
            if pay.journal_id.related_company:
                pay.outstanding_account_id = pay.journal_id.loan_entry_account_id
            else:
                if pay.journal_id.transitional_exception:
                    pay.outstanding_account_id = pay.journal_id.default_account_id

    def _get_valid_liquidity_accounts(self):
        res = super(AccountPayment, self)._get_valid_liquidity_accounts()
        if self.journal_id.related_company:
            res |= self.journal_id.loan_entry_account_id
        return res

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)

        if self.journal_id.related_company:
            line_to_edit = next((item for item in res if item["account_id"] == self.outstanding_account_id.id), None)
            line_to_edit['partner_id'] = self.journal_id.related_company.partner_id.id

        return res
    
    def _synchronize_from_moves(self, changed_fields):
        ''' Override to change the validation of same partner when there is involved a intercompany payment.
        Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one outstanding payments/receipts account.",
                        move.display_name,
                    ))

                if len(counterpart_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one receivable/payable account (with an exception of "
                        "internal transfers).",
                        move.display_name,
                    ))

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, "
                        "all optional journal items must share the same account.",
                        move.display_name,
                    ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in
                       all_lines) and not pay.journal_id.related_company:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))



