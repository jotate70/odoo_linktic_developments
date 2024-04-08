from odoo import fields, _, models, api
from odoo.exceptions import ValidationError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    transitional_exception = fields.Boolean(string="Transitional Exception", default=False)
    related_company = fields.Many2one(comodel_name='res.company', string='Related Company', domain="[('id', '!=', company_id)]")
    loan_entry_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Loan Entry Account', domain="[('company_id', '=', company_id)]")
    loan_exit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Loan Exit Account', domain="[('company_id', '=', company_id)]")
    journal_credit = fields.Boolean(string='Journal Credit')
    purchase_type_journal = fields.Selection(selection=[('purchase', 'Purchase'),
                                                        ('credit_card', 'Credit Card'),
                                                        ('advance', 'Advance'),
                                                        ('Equivalent Document', 'Equivalent Document'),
                                                        ('others', 'Others')],
                                             copy=True, required=True,
                                             string='Type Type Journal')
    payslip_journal = fields.Boolean(string="Payslip Journal", default=False)

    @api.onchange('type')
    def _compute_purchase_type_journal(self):
        if self.type == 'purchase':
            self.purchase_type_journal = 'purchase'
        else:
            self.purchase_type_journal = 'others'
        self.payslip_journal = False

    @api.onchange('purchase_type_journal')
    def _compute_journal_credit(self):
        if self.purchase_type_journal == 'credit_card':
            self.journal_credit = True
        else:
            self.journal_credit = False

    @api.constrains('related_company')
    def unique_inter_company_journal(self):
        for record in self:
            if record.related_company:
                if self.env['account.journal'].search_count([('related_company', '=', record.related_company.id)]) > 1:
                    old_journal_associated = self.env['account.journal'].search(
                        [('related_company', '=', record.related_company.id), ('id', '!=', record.id)])
                    raise ValidationError(
                        _(f"Company '{record.related_company.name}' is already associated to journal '{old_journal_associated.name}'."))

    @api.onchange('related_company')
    def reset_loan_accounts(self):
        for record in self:
            if not record.related_company:
                record.loan_entry_account_id = False
                record.loan_exit_account_id = False

   # ///////////////////////////////////////////////// NEW CODE ///////////////////////////////////////////

    def action_open_batch_payment(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id,
                    'default_journal_id': self.id})
        return {
            'name': _('Create Batch Payment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.batch.payment',
            'context': ctx,
        }

    # def _default_inbound_payment_methods(self):
    #     res = super()._default_inbound_payment_methods()
    #     return res | self.env.ref('linktic_payments.account_payment_method_batch_deposit_2')

    @api.model
    def _create_batch_payment_outbound_sequence(self):
        IrSequence = self.env['ir.sequence']
        if IrSequence.search([('code', '=', 'account.outbound.batch.payment')]):
            return
        return IrSequence.sudo().create({
            'name': _("Outbound Batch Payments Sequence"),
            'padding': 4,
            'code': 'account.outbound.batch.payment',
            'number_next': 1,
            'number_increment': 1,
            'use_date_range': True,
            'prefix': 'BATCH/OUT/%(year)s/',
            # by default, share the sequence for all companies
            'company_id': False,
        })

    @api.model
    def _create_batch_payment_inbound_sequence(self):
        IrSequence = self.env['ir.sequence']
        if IrSequence.search([('code', '=', 'account.inbound.batch.payment')]):
            return
        return IrSequence.sudo().create({
            'name': _("Inbound Batch Payments Sequence"),
            'padding': 4,
            'code': 'account.inbound.batch.payment',
            'number_next': 1,
            'number_increment': 1,
            'use_date_range': True,
            'prefix': 'BATCH/IN/%(year)s/',
            # by default, share the sequence for all companies
            'company_id': False,
        })

