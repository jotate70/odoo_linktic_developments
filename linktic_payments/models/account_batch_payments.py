# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class BatchPayment(models.Model):
    _name = "account.batch.payment"
    _description = "Batch Payment"
    _order = "priority desc, date desc, id desc"

    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True, copy=False,
                       string='Reference', readonly=True,
                       default='New', store=True,
                       states={'draft': [('readonly', False)]})
    priority = fields.Selection(selection=[('0', 'All'),
                                           ('1', 'Low priority'),
                                           ('2', 'High priority'),
                                           ('3', 'Urgent')],
                                string='Priority', default='0', index=True)
    date = fields.Date(required=True, copy=False,
                       default=fields.Date.context_today, readonly=True,
                       states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[('draft', 'New'),
                                        ('sent', 'Sent'),
                                        ('reconciled', 'Reconciled')],
                             store=True, compute='_compute_state', default='draft')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Bank',
                                 domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]", required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    payment_ids = fields.One2many(comodel_name='account.payment', inverse_name='batch_payment_id',
                                  string="Payments", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    amount = fields.Monetary(compute='_compute_amount',
                             store=True, readonly=True)
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  compute='_compute_currency',
                                  store=True, readonly=True)
    batch_type = fields.Selection(selection=[('inbound', 'Inbound'),
                                             ('outbound', 'Outbound')],
                                  required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default='inbound')
    payment_method_id = fields.Many2one(comodel_name='account.payment.method',
                                        string='Payment Method', store=True,
                                        readonly=False,
                                        compute='_compute_payment_method_id',
                                        domain="[('id', 'in', available_payment_method_ids)]",
                                        help="The payment method used by the payments in this batch.")
    available_payment_method_ids = fields.Many2many(comodel_name='account.payment.method',
                                                    compute='_compute_available_payment_method_ids')
    payment_method_code = fields.Char(related='payment_method_id.code', readonly=False)
    description = fields.Text(string='Description', size=40, default='BATCH PAYMENTS')

    def action_compute_draft_state(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.model
    def _get_batch_payment_name(self):
        if self.batch_type == 'inbound':
            self.name = self.env['ir.sequence'].next_by_code('account.inbound.batch.payment') or 'New'
        if self.batch_type == 'outbound':
            self.name = self.env['ir.sequence'].next_by_code('account.outbound.batch.payment') or 'New'

    def action_validate_batch_button(self):
        self.ensure_one()
        self._get_batch_payment_name()
        if not self.payment_ids:
            raise UserError(_("Cannot validate an empty batch. Please add some payments to it first."))
        return self._send_after_validation()

    @api.depends('batch_type', 'payment_ids', 'journal_id')
    def _compute_payment_method_id(self):
        for batch in self:
            if batch.payment_ids:
                batch.payment_method_id = batch.payment_ids.payment_method_line_id[0].payment_method_id
                continue
            if not batch.journal_id:
                batch.available_payment_method_ids = False
                batch.payment_method_id = False
                continue
            available_payment_method_lines = batch.journal_id._get_available_payment_method_lines(batch.batch_type)
            batch.available_payment_method_ids = available_payment_method_lines.mapped('payment_method_id')
            # Select the first available one by default.
            if batch.available_payment_method_ids:
                batch.payment_method_id = batch.available_payment_method_ids[0]._origin
            else:
                batch.payment_method_id = False

    @api.depends('batch_type', 'journal_id')
    def _compute_available_payment_method_ids(self):
        for batch in self:
            available_payment_method_lines = batch.journal_id._get_available_payment_method_lines(batch.batch_type)
            batch.available_payment_method_ids = available_payment_method_lines.mapped('payment_method_id')

    @api.depends('payment_ids.move_id.is_move_sent', 'payment_ids.is_matched')
    def _compute_state(self):
        for batch in self:
            if batch.payment_ids and all(pay.is_matched and pay.is_move_sent for pay in batch.payment_ids):
                batch.state = 'reconciled'
            elif batch.payment_ids and all(pay.is_move_sent for pay in batch.payment_ids):
                batch.state = 'sent'
            else:
                batch.state = 'draft'

    @api.depends('journal_id')
    def _compute_currency(self):
        for batch in self:
            if batch.journal_id:
                batch.currency_id = batch.journal_id.currency_id or batch.journal_id.company_id.currency_id
            else:
                batch.currency_id = False

    @api.depends('date', 'currency_id', 'payment_ids.amount')
    def _compute_amount(self):
        for batch in self:
            currency = batch.currency_id or batch.journal_id.currency_id or self.env.company.currency_id
            date = batch.date or fields.Date.context_today(self)
            amount = 0
            for payment in batch.payment_ids:
                liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                for line in liquidity_lines:
                    if line.currency_id == currency:
                        amount += line.amount_currency
                    else:
                        amount += line.company_currency_id._convert(line.balance, currency, line.company_id, date)
            batch.amount = amount

    @api.constrains('batch_type', 'journal_id', 'payment_ids')
    def _check_payments_constrains(self):
        for record in self:
            all_companies = set(record.payment_ids.mapped('company_id'))
            if len(all_companies) > 1:
                raise ValidationError(_("All payments in the batch must belong to the same company."))
            all_journals = set(record.payment_ids.mapped('journal_id'))
            if len(all_journals) > 1 or (record.payment_ids and record.payment_ids[:1].journal_id != record.journal_id):
                raise ValidationError(_("The journal of the batch payment and of the payments it contains must be the same."))
            all_types = set(record.payment_ids.mapped('payment_type'))
            if all_types and record.batch_type not in all_types:
                raise ValidationError(_("The batch must have the same type as the payments it contains."))
            all_payment_methods = record.payment_ids.payment_method_id
            if len(all_payment_methods) > 1:
                raise ValidationError(_("All payments in the batch must share the same payment method."))
            if all_payment_methods and record.payment_method_id not in all_payment_methods:
                raise ValidationError(_("The batch must have the same payment method as the payments it contains."))
            payment_null = record.payment_ids.filtered(lambda p: p.amount == 0)
            if payment_null:
                names = '\n'.join([p.name or _('Id: %s', p.id) for p in payment_null])
                msg = _('You cannot add payments with zero amount in a Batch Payment.\nPayments:\n%s', names)
                raise ValidationError(msg)
            non_posted = record.payment_ids.filtered(lambda p: p.state != 'posted')
            if non_posted:
                names = '\n'.join([p.name or _('Id: %s', p.id) for p in non_posted])
                msg = _('You cannot add payments that are not posted.\nPayments:\n%s', names)
                raise ValidationError(msg)

    def _send_after_validation(self):
        self.ensure_one()
        if self.payment_ids:
            self.payment_ids.mark_as_sent()

    def check_payments_for_errors(self):
        self.ensure_one()
        #We first try to post all the draft batch payments
        rslt = self._check_and_post_draft_payments(self.payment_ids.filtered(lambda x: x.state == 'draft'))
        wrong_state_payments = self.payment_ids.filtered(lambda x: x.state != 'posted')
        if wrong_state_payments:
            rslt.append({
                'title': _("Payments must be posted to be added to a batch."),
                'records': wrong_state_payments,
                'help': _("Set payments state to \"posted\".")
            })

        sent_payments = self.payment_ids.filtered(lambda x: x.is_move_sent)
        if sent_payments:
            rslt.append({
                'title': _("Some payments have already been sent."),
                'records': sent_payments,
            })

        if self.batch_type == 'inbound':
            pmls = self.journal_id.inbound_payment_method_line_ids
            default_payment_account = self.journal_id.company_id.account_journal_payment_debit_account_id
        else:
            pmls = self.journal_id.outbound_payment_method_line_ids
            default_payment_account = self.journal_id.company_id.account_journal_payment_credit_account_id
        pmls = pmls.filtered(lambda x: x.payment_method_id == self.payment_method_id)
        no_statement_reconciliation = self.journal_id.default_account_id == (pmls.payment_account_id[:1] or default_payment_account)
        bank_reconciled_payments = self.payment_ids.filtered(lambda x: x.is_matched)
        if bank_reconciled_payments and not no_statement_reconciliation:
            rslt.append({
                'title': _("Some payments have already been matched with a bank statement."),
                'records': bank_reconciled_payments,
            })

        return rslt

    def _check_and_post_draft_payments(self, draft_payments):
        exceptions_mapping = {}
        for payment in draft_payments:
            try:
                payment.action_post()
            except UserError as e:
                name = e.args[0]
                if name in exceptions_mapping:
                    exceptions_mapping[name] += payment
                else:
                    exceptions_mapping[name] = payment

        return [{'title': error, 'records': pmts} for error, pmts in exceptions_mapping.items()]

