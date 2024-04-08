# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CardMovementRecords(models.Model):
    _name = "card_movement_records"
    _description = "card movement records"
    _order = "date desc, id desc"

    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[('draft', 'New'),
                                        ('done', 'Done'),
                                        ('reconciled', 'Reconciled')],
                             store=True, default='draft', string='State')
    name = fields.Char(required=True, copy=False,
                       string='Card Name', readonly=True,
                       default='New', store=True,
                       states={'draft': [('readonly', False)]})
    partner_name = fields.Char(required=True, string='Partner Name', store=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    date = fields.Date(required=True, string='Date')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          store=True)
    description = fields.Text(string='Description')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    ultimas4 = fields.Char(string='ULTIMAS4')
    pay_mode = fields.Selection(selection=[('physical', 'physical'),
                                           ('virtual', 'virtual')],
                                default='draft', string='Pay Mode')
    card_type = fields.Selection(selection=[('debit', 'Debit'),
                                            ('credit', 'Credit')],
                                 default='credit', required=True, store=True,
                                 string='Card Type')
    amount = fields.Monetary(store=True, string='Amount')
    currency_id = fields.Many2one(comodel_name='res.currency', store=True, readonly=True,
                                  default=lambda self: self.env.company.currency_id)
    ceco = fields.Char(string='CECO')
    pay_date = fields.Date(required=True, string='Pay Date')



