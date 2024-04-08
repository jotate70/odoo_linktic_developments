# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    travel_request1_id = fields.Many2one(comodel_name='travel.request', string='Travel Request 1')
    travel_request2_id = fields.Many2one(comodel_name='travel.request', string='Travel Request 2')
    travel_expense = fields.Boolean(string='is a travel expense', default=False)
    identification_id = fields.Char(string='Nº identificación', related='employee_id.identification_id')
    name = fields.Char(copy=False, default='New', readonly=True)
    hr_summary_items_id = fields.One2many(comodel_name='hr_items_info', inverse_name='expense_sheet_id',
                                          string='Agrupación Items')
    hr_summary_analytic_account_id = fields.One2many(comodel_name='hr_analytic_account_info',
                                                     inverse_name='expense_sheet_id', string='Agrupación cuenta analítica')
    hr_summary_contact_id = fields.One2many(comodel_name='hr_third_info', inverse_name='expense_sheet_id',
                                            string='Agrupación proveedor')

    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        for sheet in self:
            if sheet.travel_expense == True:
                pass
            else:
                return super(HrExpenseSheet, self)._check_employee()

    def action_submit_sheet(self):
        for rec in self.expense_line_ids:
            if not rec.supplier_id and not rec.supplier_vat:
                rec.write({'supplier_id': self.employee_id.sudo().address_home_id.commercial_partner_id.id,
                           'supplier_vat': self.identification_id})
        self.write({'state': 'submit'})
        self.activity_update()
        self.select_summary_items_id()
        self.select_compute_analytic_account_id()
        self.select_compute_summary_contact_id()

    def reset_expense_sheets(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.mapped('expense_line_ids').write({'is_refused': False})
        self.write({'state': 'draft', 'approval_date': False})
        self.activity_update()
        # Reset field
        self.hr_summary_items_id = False
        self.hr_summary_analytic_account_id = False
        self.hr_summary_contact_id = False
        return True

    # Herencia del modelo cretae para crear secuencias
    @api.model
    def create(self, vals):
        # Codigo adicional
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('expense.ifpv') or 'New'
        result = super(HrExpenseSheet, self).create(vals)
        return result

    def select_summary_items_id(self):
        a = []
        b = []
        analytic_cost = 0
        for rec1 in self.expense_line_ids:
            if rec1.product_id:
                a.append(rec1.product_id.id)
                b = list(set(a))
        for rec2 in b:
            analytic_cost = 0
            for rec3 in self.expense_line_ids:
                if rec2 == rec3.product_id.id:
                    analytic_cost += rec3.total_amount
            self.write({'hr_summary_items_id': [(0, 0, {'expense_sheet_id': rec3.id,
                                                        'company_id': rec3.company_id.id,
                                                        'travel_request_id': rec3.travel_id.id or rec3.travel_expence_id.id,
                                                        'product_id': rec2,
                                                        'employee_id': self.employee_id.id,
                                                        'supplier_id': rec3.supplier_id.id,
                                                        'supplier_type': rec3.supplier_type.id,
                                                        'supplier_vat': rec3.supplier_vat,
                                                        'analytic_tag_ids': rec3.analytic_tag_ids.id,
                                                        'amount_total': analytic_cost,
                                                        'currency_id': rec3.currency_id.id,
                                                        'mode': 'items',
                                                        })]})

    def select_compute_analytic_account_id(self):
        a = []
        b = []
        analytic_cost = 0
        for rec1 in self.expense_line_ids:
            if rec1.analytic_account_id:
                a.append(rec1.analytic_account_id.id)
                b = list(set(a))
        for rec2 in b:
            analytic_cost = 0
            for rec3 in self.expense_line_ids:
                if rec2 == rec3.analytic_account_id.id:
                    analytic_cost += rec3.total_amount
            self.write({'hr_summary_analytic_account_id': [(0, 0, {'expense_sheet_id': rec3.id,
                                                                   'company_id': rec3.company_id.id,
                                                                   'travel_request_id': rec3.travel_id.id or rec3.travel_expence_id.id,
                                                                   'product_id': rec3.product_id.id,
                                                                   'employee_id': self.employee_id.id,
                                                                   'supplier_type': rec3.supplier_type.id,
                                                                   'supplier_vat': rec3.supplier_vat,
                                                                   'analytic_account_id': rec2,
                                                                   'analytic_tag_ids': rec3.analytic_tag_ids.id,
                                                                   'amount_total': analytic_cost,
                                                                   'currency_id': rec3.currency_id.id,
                                                                   'mode': 'analytic_account',
                                                            })]})

    def select_compute_summary_contact_id(self):
        a = []
        b = []
        aa = []
        bb = []
        l = []
        analytic_cost = 0
        c = 0
        for rec1 in self.expense_line_ids:
            if rec1.supplier_id:
                a.append(rec1.supplier_id.id)
                aa.append(rec1.supplier_vat)
                b = list(a)
                bb = list(aa)

        for rec2 in b:
            analytic_cost = 0
            vat = bb[c]
            c += 1
            for rec3 in self.expense_line_ids:
                if rec2 == rec3.supplier_id.id:
                    analytic_cost += rec3.total_amount
            self.write({'hr_summary_contact_id': [(0, 0, {'expense_sheet_id': rec3.id,
                                                          'company_id': rec3.company_id.id,
                                                          'travel_request_id': rec3.travel_id.id or rec3.travel_expence_id.id,
                                                          'product_id': rec3.product_id.id,
                                                          'employee_id': self.employee_id.id,
                                                          'supplier_id': rec2,
                                                          'supplier_type': rec3.supplier_type.id,
                                                          'supplier_vat': vat,
                                                          'analytic_tag_ids': rec3.analytic_tag_ids.id,
                                                          'amount_total': analytic_cost,
                                                          'currency_id': rec3.currency_id.id,
                                                          'mode': 'supplier',
                                                          })]})
    # Compute state to done for travel request
    def action_legalize_advance_expense_sheet(self):
        res = super(HrExpenseSheet, self).action_legalize_advance_expense_sheet()
        if self.travel_request1_id:
            self.travel_request1_id._compute_change_sate_to_done()
        return res


