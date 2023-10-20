from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    scheduled_payment_day = fields.Date(string='Scheduled Payment Date')
    payment_journal_id = fields.Many2one('account.journal', string='Payment Bank',
                                         domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    approved_manager = fields.Boolean(string='Approved Manager')

    def write(self, vals):
        if 'approved_manager' in vals:
            if not self.env.user.has_group('account.group_account_manager'):
                raise ValidationError(_("This user doesn't have approval permissions."))

            if any(move.payment_state != 'not_paid' for move in self):
                raise ValidationError(_("Cannot change the validation state for a paid Bill."))

            if any(move.state != 'posted' for move in self):
                raise ValidationError(_("Only can change the Approval state of Posted Bills."))

        return super(AccountMove, self).write(vals)

    def action_register_payment(self):
        ''' Extend to check if payment schedule fields are configured in account move before displaying payment
        wizard'''

        if all(item in ['in_invoice', 'in_refund', 'in_receipt'] for item in self.mapped('move_type')):

            if len(self.mapped('payment_journal_id')) > 1:
                raise ValidationError(
                    _(f"There are documents with different payment bank configured, please all records should have the same bank"))

            for bill in self:
                if not bill.scheduled_payment_day:
                    raise ValidationError(_(f"The scheduled payment date in Bill ({bill.name}) must be configured"))

                if bill.scheduled_payment_day > fields.Date.today():
                    raise ValidationError(_(f"The scheduled payment date in Bill ({bill.name}) is after today's date"))

                if not bill.payment_journal_id:
                    raise ValidationError(
                        _(f"You must select a Payment Bank to register a payment in Bill ({bill.name})"))

                if not bill.approved_manager:
                    raise ValidationError(
                        _(f"To register a payment in the Bill ({bill.name}) must be approved by manager"))

                last_journal = bill.payment_journal_id

        res = super(AccountMove, self).action_register_payment()

        if all(item in ['in_invoice', 'in_refund', 'in_receipt'] for item in self.mapped('move_type')):
            res.get('context')['default_journal_id'] = last_journal.id

        return res

    def action_schedule_payment(self):
        """ Returns an action opening the schedule payment wizard."""
        moves = self.env['account.move'].browse(self._context.get('active_ids'))

        non_posted_moves = moves.filtered(lambda m: m.state != 'posted')
        paid_moves = moves.filtered(lambda m: m.payment_state != 'not_paid')

        if non_posted_moves:
            raise ValidationError(
                _(f"Only posted bill can get a payment schedule, the following bills are not posted:\n {non_posted_moves.mapped('name')}"))

        if paid_moves:
            raise ValidationError(
                _(f"Cannot change a scheduled payment from a paid bill, the following bills has been paid:\n {paid_moves.mapped('name')}"))

        new_wizard = self.env['account.payment.scheduler'].create({
            'active_move_ids': [(6, 0, moves.ids)],
            'scheduled_payment_day': fields.Date.today(),
            'company_id': moves.mapped('company_id')[0],
        })
        return {
            'name': _('Schedule Payment'),
            'view_mode': 'form',
            'res_model': 'account.payment.scheduler',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def approve_bills(self):
        moves = self.env['account.move'].browse(self._context.get('active_ids'))

        non_posted_moves = moves.filtered(lambda m: m.state != 'posted')
        paid_moves = moves.filtered(lambda m: m.payment_state != 'not_paid')

        if non_posted_moves:
            raise ValidationError(
                _(f"Only posted bill can get approved, the following bills are not posted:\n {non_posted_moves.mapped('name')}"))

        if paid_moves:
            raise ValidationError(
                _(f"Cannot approve a paid bill, the following bills has been paid:\n {paid_moves.mapped('name')}"))

        moves.approved_manager = True
