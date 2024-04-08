# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
import json

class HrHotelInfo(models.Model):
    _name = "hr_hotel_info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hotel Reservation"
    _order = "id desc"

    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    travel_request_id = fields.Many2one(comodel_name='travel.request', string='Solicitud de viaje')
    product_id = fields.Many2one(comodel_name='product.product', string="Hospedaje",
                                 domain=[('can_be_expensed', '=', True)], required=True)
    name = fields.Char(string="Descripción", required=True)
    hotel_type = fields.Selection([('hotel', 'Hotel'),
                                   ('hostel', 'Hostal'),
                                   ('apart-hotel', 'Apart-Hotel'),
                                   ('apartment', 'Apartmento'),
                                   ('business_hotel', 'Business Hotel')], string="Tipo de hospedaje", default='hotel')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', string="Cuenta Analítica")
    street = fields.Char('Dirección')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one(comodel_name='res.country.state', string="Estado")
    country_id = fields.Many2one(comodel_name='res.country', string="País")

    req_departure_date = fields.Datetime(string="Fecha de entrada", required=True)
    req_return_date = fields.Datetime(string="Fecha de salida")
    days = fields.Char(string='Días', compute="_compute_days")
    amount_total = fields.Monetary(string='Costo', currency_field='currency_id', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True,
                                  default=lambda self: self.env.company.currency_id)
    supplier_id = fields.Many2one(comodel_name='res.partner', string='Proveedor')
    supplier_type = fields.Many2one(comodel_name='l10n_latam.identification.type',
                                    string='Tipo de documento',
                                    help='Tipo de documento')
    supplier_vat = fields.Char(string='Nº identificación', help='Número de Documento')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('on_aprobation', 'On Approval'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('submitted', 'Expenses Submitted'),
                              ('cancel', 'Cancelado')], default="draft", string="Estado")
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    # Aditional fields
    general_budget_domain = fields.Char(string='Domain budget position', compute='_compute_account_analytic_domain')
    general_budget_id = fields.Many2one(comodel_name='account.budget.post', string='Budgetary Position',
                                        domain='general_budget_domain')
    budget_line_segregation_id = fields.Many2one(comodel_name='crossovered.budget.lines.segregation',
                                                 string='Budget Line Segregation',
                                                 domain="[('general_budget_id', '=?', general_budget_id), ('analytic_account_id', '=?', account_analytic_id)]")
    segregation_balance = fields.Monetary(string="Balance", compute="get_segregation_balance", store=True, readonly=True)
    purchase_request_ids = fields.One2many(comodel_name='purchase.request',
                                           inverse_name='hr_hotel_info_id',
                                           string='Requisiciones')
    count_purchase_request = fields.Integer(string='Count Purchase Request', compute='_compute_count_purchase_request')
    employee_ids = fields.Many2many(comodel_name='hr.employee', string='Empleados')
    number_people = fields.Integer(string='Número de personas', compute='_compute_count_number_people')

    # function domain dynamic
    @api.depends('account_analytic_id')
    def _compute_account_analytic_domain(self):
        for rec in self:
            if rec.account_analytic_id:
                vat = rec.env['crossovered.budget.lines.segregation'].search(
                    [('analytic_account_id', 'in', rec.account_analytic_id.ids)])
                rec.general_budget_domain = json.dumps([('id', 'in', list(set(vat.general_budget_id.ids)))])
            else:
                rec.general_budget_domain = json.dumps([()])

    @api.depends('budget_line_segregation_id')
    def get_segregation_balance(self):
        for record in self:
            if record.budget_line_segregation_id:
                record.segregation_balance = (record.budget_line_segregation_id.planned_amount - record.budget_line_segregation_id.practical_amount) * -1
            else:
                record.segregation_balance = 0

    @api.depends('employee_ids')
    def _compute_count_number_people(self):
        for rec in self:
            if rec.employee_ids:
                for rec2 in rec.employee_ids:
                    rec.number_people += 1
            else:
                rec.number_people = 0

    @api.onchange('product_id','hotel_type','city','req_departure_date','req_return_date')
    def _compute_name_get(self):
        for rec in self:
            name = (str(rec.product_id.name) + ' [ ' + str(rec.hotel_type) + ' ] ' + ' [ ' + str(
                rec.city) + ' ] ' + ' [ ' + str(rec.req_departure_date) + ' --> ' + str(
                        rec.req_return_date)) + ' ] '
            rec.name = name
            rec.account_analytic_id = rec.travel_request_id.account_analytic_id
            rec.general_budget_id = rec.travel_request_id.general_budget_id
            rec.budget_line_segregation_id = rec.travel_request_id.budget_line_segregation_id
            rec.product_id = rec.env['product.product'].search([('product_expense_type', '=', 'accommodation')], limit=1)
            if not self.employee_ids:
                rec.employee_ids = rec.travel_request_id.employee_id

    def _compute_count_purchase_request(self):
        if self.purchase_request_ids:
            for rec in self.purchase_request_ids:
                self.count_purchase_request += 1
        else:
            self.count_purchase_request = 0

    @api.onchange('supplier_id')
    def _compute_select_supplier(self):
        self.supplier_type = self.supplier_id.l10n_latam_identification_type_id
        self.supplier_vat = self.supplier_id.vat

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr_travel_info'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense._origin.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'hr_travel_info'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr_travel_info', 'default_res_id': self.id}
        return res

    @api.depends('req_departure_date', 'req_return_date')
    def _compute_days(self):
        for line in self:
            line.days = False
            if line.req_departure_date and line.req_return_date:
                diff = line.req_return_date - line.req_departure_date
                mini = diff.seconds // 60
                hour = mini // 60
                sec = (diff.seconds) - (mini * 60)
                miniute = mini - (hour * 60)
                # time = str(diff.days) + ' Days, ' + ("%d:%02d.%02d" % (hour, miniute, sec))
                time = str(diff.days) + ' Days'
                line.days = time
                # return
            else:
                line.days = 0
                # return
