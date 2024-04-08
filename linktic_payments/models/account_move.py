from odoo import fields, _, models, api
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    priority = fields.Selection(selection=[('0', 'All'),
                                           ('1', 'Low priority'),
                                           ('2', 'High priority'),
                                           ('3', 'Urgent')],
                                string='Priority', tracking=True,
                                index=True)
    scheduled_payment_day = fields.Date(string='Scheduled Payment Date',
                                        tracking=True)
    payment_journal_id = fields.Many2one(comodel_name='account.journal', string='Programmed Payment',
                                         domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]",
                                         tracking=True)
    approved_manager = fields.Boolean(string='Approved Manager', tracking=True)
    approved_vice_president = fields.Boolean(string='Approved vice-president', tracking=True)
    approved_advisor = fields.Boolean(string='Approved advisor', tracking=True)
    approved_date_payment = fields.Datetime(string='Approved Date Payment', tracking=True)
    payment_bank_related_id = fields.Many2one(comodel_name='account.journal', string='Payment Bank',
                                              related='payment_id.journal_id', tracking=True)
    payment_check = fields.Boolean(string='Payment Check', related='payment_id2.payment_check')
    payment_date_related = fields.Date(string='Payment date', related='payment_id2.date', store=True)
    payment_method_line_id = fields.Many2one(comodel_name='account.payment.method.line', string='Payment Method',
                                             store=True)
    approved_vice_president_id = fields.Many2one(comodel_name='res.users', string='Approved vice-president',
                                                 related='company_id.approved_vice_president_id')
    approved_advisor_id = fields.Many2one(comodel_name='res.users', string='Approved advisor_employee_id',
                                          related='company_id.approved_advisor_id')
    active_user = fields.Boolean(string='Active User', compute='_compute_user_available')
    active_user2 = fields.Boolean(string='Active User 2', compute='_compute_user_available_2')
    analytic_account_ids = fields.Many2many(comodel_name='account.analytic.account',
                                            relation='x_account_analytic_to_account_move_rel',
                                            column1='account_move_id',
                                            column2='account_analytic_id',
                                            string='Account Analytic', compute_sudo=False,
                                            compute='_compute_select_account_analytic',
                                            search='_search_select_account_analytic')
    analytic_account_ids2 = fields.Many2many(comodel_name='account.analytic.account',
                                            relation='x_account_analytic_to_account_move_rel',
                                            column1='account_move_id',
                                            column2='account_analytic_id',
                                            string='Account Analytic')
    payment_id2 = fields.Many2one(comodel_name='account.payment', string="Payment")
    analytic_account_name = fields.Char(string='Account Analytic Name')
    date_payment = fields.Date(related='payment_id2.date', store=True)
    purchase_type_journal = fields.Selection(selection=[('purchase', 'Purchase'),
                                                        ('credit_card', 'Credit Card'),
                                                        ('advance', 'Advance'),
                                                        ('Equivalent Document', 'Equivalent Document'),
                                                        ('others', 'Others')],
                                             related='journal_id.purchase_type_journal',
                                             string='Type Type Journal')

    @api.onchange('invoice_payment_term_id')
    def _compute_select_journal_credit(self):
        if self.invoice_payment_term_id.term_type == 'credit_type':
            data = self.env['account.journal'].search([('journal_credit', '=', True)], limit=1)
            self.journal_id = data

    @api.depends('invoice_line_ids')
    def _compute_select_account_analytic(self):
        for rec in self:
            data = ""
            if rec.invoice_line_ids:
                vat = rec.mapped('invoice_line_ids').analytic_account_id
                rec.analytic_account_ids = vat
                rec.analytic_account_ids2 = vat
                for rec2 in vat:
                    if len(vat) > 1:
                        data += rec2.name + ', '
                    else:
                        data += rec2.name
                rec.analytic_account_name = data
            else:
                rec.analytic_account_name = False
                rec.analytic_account_ids = False

    def _search_select_account_analytic(self, operator, value):
        value_1 = value.upper() or '' # Convierte a mayuscula
        vat = []
        name = self.env['account.analytic.account'].search([('name', '=', value_1)])
        data = self.env['account.move'].search([('analytic_account_ids', 'in', name.ids)])
        if data:
            for rec in data:
                vat.append(rec.id)
        else:
            vat = []
        return [('id', 'in', vat)]

    api.depends('approved_vice_president_id')
    def _compute_user_available(self):
        if self.approved_vice_president_id in self.env.user:
            self.active_user = True
        else:
            self.active_user = False

    api.depends('approved_vice_president_id')

    def _compute_user_available_2(self):
        if self.approved_advisor_id in self.env.user:
            self.active_user2 = True
        else:
            self.active_user2 = False

    def action_form_account_move(self):
        """ Returns an action account move form."""
        return {
            'name': _('Priority Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
        }

    def _compute_select_payment_method_line_id(self, vat, vat2):
        for rec in self:
            rec.write({'payment_method_line_id': vat})
            rec.write({'payment_method_id': vat2})

    def action_select_payment_method_wizard(self):
        """ Returns an action opening payment method wizard."""
        moves = self.env['account.move'].browse(self._context.get('active_ids'))
        new_wizard = self.env['account.payment.method.wizard'].create({
            'account_move_ids': [(6, 0, moves.ids)],
        })
        return {
            'name': _('Payment method'),
            'view_mode': 'form',
            'res_model': 'account.payment.method.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    def _compute_select_priority(self, vat):
        for rec in self:
            rec.write({'priority': vat})

    def action_select_priority(self):
        """ Returns an action opening priority wizard."""
        moves = self.env['account.move'].browse(self._context.get('active_ids'))
        new_wizard = self.env['account.payment.priority'].create({
            'account_move_ids': [(6, 0, moves.ids)],
        })
        return {
            'name': _('Priority Payment'),
            'view_mode': 'form',
            'res_model': 'account.payment.priority',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': new_wizard.id,
        }

    @api.onchange('approved_manager')
    def _compute_approved_date_payment(self):
        if self.approved_manager == True:
            self.write({'approved_date_payment': fields.datetime.now()})

    def write(self, vals):
        if 'approved_manager' in vals:
            if not self.env.user.has_group('account.group_account_manager'):
                raise ValidationError(_("This user doesn't have approval permissions."))

            if any(move.payment_state != 'not_paid' for move in self):
                raise ValidationError(_("Cannot change the validation state for a paid Bill."))

            if any(move.state != 'posted' for move in self):
                raise ValidationError(_("Only can change the Approval state of Posted Bills."))

        return super(AccountMove, self).write(vals)

    def action_form_account_payment(self):
        """ Returns an action account move form."""
        if self.payment_id:
            return {
                'name': _('Payment'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.payment_id.id,
            }

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

                if not bill.approved_manager and self.invoice_payment_term_id.term_type != 'credit_type':
                    raise ValidationError(
                        _(f"To register a payment in the Bill ({bill.name}) must be approved by manager"))

                last_journal = bill.payment_journal_id

        res = super(AccountMove, self).action_register_payment()

        if all(item in ['in_invoice', 'in_refund', 'in_receipt'] for item in self.mapped('move_type')):
            res.get('context')['default_journal_id'] = last_journal.id

        self.action_form_account_payment()

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
        moves.approved_date_payment = fields.datetime.now()

    def action_register_approved_vice_president(self):
        moves = self.env['account.move'].browse(self._context.get('active_ids'))
        if moves[0].approved_vice_president_id == self.env.user:
            moves.approved_vice_president = True
        else:
            raise ValidationError("You are not responsible for approval")

    def action_register_approved_advisor(self):
        moves = self.env['account.move'].browse(self._context.get('active_ids'))
        if moves[0].approved_advisor_id == self.env.user:
            moves.approved_advisor = True
        else:
            raise ValidationError("You are not responsible for approval")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    category_id = fields.Many2one(comodel_name='res.partner.category')
    category = fields.Char(compute='_compute_category', store=True)

    @api.depends('partner_id')
    def _compute_category(self):
        for record in self:
            record.category = record.partner_id.category_id[0].name if record.partner_id.category_id else _(
                'Not Applicable')
