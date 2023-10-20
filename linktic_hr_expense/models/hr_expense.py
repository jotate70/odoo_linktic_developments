from odoo import fields, _, models, api, Command
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from odoo.tools.misc import clean_context, format_date


class HrExpense(models.Model):
    _inherit = "hr.expense"

    payment_mode = fields.Selection(selection_add=[("payment_advance", "Payment Advance")])
    payment_advance_id = fields.Many2one('hr.expense.advance', string="Advance",
                                         domain="[('state', '=', 'to_pay'), ('employee_id', '=', employee_id)]")

    def action_submit_expenses(self):
        res = super(HrExpense, self).action_submit_expenses()
        if self.payment_mode == 'payment_advance':
            expense_sheet = self.env['hr.expense.sheet'].search(
                [('payment_advance_id', '=', self.payment_advance_id.id)])

            if expense_sheet:
                if expense_sheet.state != 'draft':
                    raise ValidationError(
                        _("The advance used in this expense is in a processed expense sheet, please revert it to draft if possible and retry"))

                expense_sheet.expense_line_ids = [(4, self.id)]
                res['res_id'] = expense_sheet.id
                del res['context']

        return res

    def _get_default_expense_sheet_values(self):
        """override method to change the computation on variable t0do, adding the new payment method """
        if any(expense.state != 'draft' or expense.sheet_id for expense in self):
            raise UserError(_("You cannot report twice the same line!"))
        if len(self.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in self):
            raise UserError(_("You can not create report without category."))

        todo = self.filtered(lambda x: x.payment_mode == 'own_account') or self.filtered(
            lambda x: x.payment_mode == 'company_account') or self.filtered(
            lambda x: x.payment_mode == 'payment_advance')
        if len(todo) == 1:
            expense_name = todo.name
        else:
            dates = todo.mapped('date')
            min_date = format_date(self.env, min(dates))
            max_date = format_date(self.env, max(dates))
            expense_name = min_date if max_date == min_date else "%s - %s" % (min_date, max_date)

        values = {
            'default_company_id': self.company_id.id,
            'default_employee_id': self[0].employee_id.id,
            'default_name': expense_name,
            'default_expense_line_ids': [Command.set(todo.ids)],
            'default_state': 'draft',
            'create': False,
            'default_payment_advance_id': self.payment_advance_id.id,
        }
        return values

    def _get_account_move_line_advances_values(self):
        # move_line_values_by_expense = {}
        move_line_values = []
        total_amount = 0.0
        total_amount_currency = 0.0
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            unit_amount = expense.unit_amount or expense.total_amount
            quantity = expense.quantity if expense.unit_amount else 1
            taxes = expense.tax_ids.with_context(round=True).compute_all(unit_amount, expense.currency_id,quantity,expense.product_id)
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

        # Advance Value Line
        employee_contact = self.employee_id.sudo().address_home_id.with_company(self.company_id)

        move_line_dst = {
            'name': _("Payment Advance"),
            'debit': 0,
            'credit': self.sheet_id.payment_advance_id.total_amount,
            'account_id': employee_contact.property_account_receivable_id.id or employee_contact.parent_id.property_account_receivable_id,
            'date_maturity': account_date,
            'amount_currency': self.sheet_id.payment_advance_id.total_amount_company,
            'currency_id': self.sheet_id.currency_id.id,
            'partner_id': partner_id,
            'exclude_from_invoice_tab': True,
        }
        move_line_values.append(move_line_dst)

        # Difference line (loss or gain)
        difference = self.sheet_id.payment_advance_id.total_amount - abs(total_amount)
        if difference != 0:
            account_dif = self.company_id.hr_expense_advance_gain_account if difference > 0 else self.company_id.hr_expense_advance_loss_account

            move_line_dst = {
                'name': _("Value Difference"),
                'debit': difference > 0 and difference,
                'credit': difference < 0 and -difference,
                'account_id': account_dif.id,
                'date_maturity': account_date,
                'amount_currency': self.sheet_id.payment_advance_id.total_amount_company - self.sheet_id.currency_id.id,
                'currency_id': self.sheet_id.currency_id.id,
                'partner_id': partner_id,
                'exclude_from_invoice_tab': True,
            }
            move_line_values.append(move_line_dst)

        return move_line_values


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    payment_advance_id = fields.Many2one('hr.expense.advance', string="Advance",
                                         domain="[('state', '=', 'to_pay'), ('employee_id', '=', employee_id)]")

    @api.constrains('payment_advance_id')
    def _validate_advance_in_expense_lines(self):
        for record in self:
            if record.payment_advance_id and any(
                    expense.payment_advance_id != record.payment_advance_id for expense in record.expense_line_ids):
                raise ValidationError(
                    _("There are expenses lines associated in this report with a different advance associated."))

    def action_submit_sheet(self):
        if self.payment_advance_id:
            all_advance_expenses = self.env['hr.expense'].search(
                [('payment_advance_id', '=', self.payment_advance_id.id), ('state', '=', 'draft')])

            if not all(item in self.expense_line_ids.ids for item in all_advance_expenses.ids):
                raise ValidationError(
                    _("In this sheet are not listed all the expenses associated to this advance, please add them or refuse non required expenses."))

        return super(HrExpenseSheet, self).action_submit_sheet()

    def action_legalize_advance_expense_sheet(self):
        """New method to make the journal entry that reconciles the advance made with the summation of all expenses
        associated to this advance"""

        journal = self.bank_journal_id if self.payment_mode == 'company_account' else self.journal_id
        account_date = self.accounting_date or fields.Date.today()
        line_values = self.expense_line_ids._get_account_move_line_advances_values()

        move_values = {
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'date': account_date,
            'ref': self.name,
            # force the name to the default value, to avoid an eventual 'default_name' in the context
            # to set it to '' which cause no number to be given to the account.move when posted.
            'name': '/',
            'line_ids': [(0, 0, line) for line in line_values]
        }

        new_move = self.env['account.move'].create(move_values)
        new_move.action_post()

        self.write({'account_move_id': new_move.id, 'state': 'done', 'payment_state': 'paid'})
        self.payment_advance_id.write({'state': 'done'})
