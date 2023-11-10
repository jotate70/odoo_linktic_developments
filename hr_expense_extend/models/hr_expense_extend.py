# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    travel_id = fields.Many2one(comodel_name='travel.request', string='Solicitud de Viaje')
    travel_expence_id = fields.Many2one(comodel_name='travel.request', string='Solicitud de Viaje')
    identification_id = fields.Char(string='Nº identificación', related='employee_id.identification_id')
    code_analytic_account_id = fields.Char(string='codigo cuenta analítica', related='analytic_account_id.code')

    actual_amount = fields.Monetary(string='Gasto real')
    amount_difference = fields.Monetary(string='Diferencia')
    supplier_id = fields.Many2one(comodel_name='res.partner', string='Proveedor')
    supplier_type = fields.Many2one(comodel_name='l10n_latam.identification.type',
                                    string='Tipo de documento',
                                    help='Tipo de documento')
    supplier_vat = fields.Char(string='Nº identificación', help='Número de Documento')
    of_refunded = fields.Boolean(string='¿Viene de un reembolso?')

    @api.onchange('supplier_id')
    def _compute_select_supplier(self):
        self.supplier_type = self.supplier_id.l10n_latam_identification_type_id
        self.supplier_vat = self.supplier_id.vat

    @api.onchange('actual_amount')
    def _compute_difference(self):
        for rec in self:
            rec.amount_difference - rec.actual_amount - rec.total_amount

    @api.onchange('product_id', 'employee_id', 'travel_expence_id')
    def _select_manager_employee_id(self):
        for rec in self:
            if rec.travel_id:
                rec.analytic_account_id = rec.travel_id.account_analytic_id
                rec.payment_mode = 'payment_advance'
                rec.payment_advance_id = rec.env['hr.expense.advance'].search([('employee_id','=',self.employee_id.ids),
                                                                                ('travel_request_id','=',self.travel_id.ids),
                                                                                ('state','=','to_pay')], limit=1)

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.date or expense.sheet_id.accounting_date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            unit_amount = expense.unit_amount or expense.total_amount
            quantity = expense.quantity if expense.unit_amount else 1
            taxes = expense.tax_ids.with_context(round=True).compute_all(unit_amount, expense.currency_id,quantity,expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            # partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id

            # ////////////////////////////////////////// NEW CODE ///////////////////////////////////////////////////
            if self.supplier_id:
                partner_id = expense.supplier_id.id
            else:
                partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id
            # ///////////////////////////////////////////////////////////////////////////////////////////////////////

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
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id,
                                                       account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id,
                                                               account_date)
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

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
                'exclude_from_invoice_tab': True,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense
