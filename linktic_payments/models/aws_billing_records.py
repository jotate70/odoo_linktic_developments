# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AWSBillingRecords(models.Model):
    _name = "aws_billing_records"
    _description = "AWS consumption and historical information storage"
    _order = "upload_date desc, id desc"

    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[('draft', 'New'),
                                        ('done', 'Done'),
                                        ('reconciled', 'Reconciled')],
                             store=True, default='draft', string='State')
    upload_date = fields.Date(string='Upload Date')
    platform_type = fields.Selection(selection=[('aws', 'AWS'),
                                                ('google_cloud', 'Google Cloud')],
                                     default='aws', required=True, store=True,
                                     string='Platform Type')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          store=True)
    value = fields.Monetary(store=True, string='Value USD')
    platform = fields.Char(string='Platform')
    star_date = fields.Date(required=True, string='Star Date')
    end_date = fields.Date(required=True, string='End Date')
    total_ppto_value = fields.Monetary(store=True, string='Total ppto value')
    month_value_ppto = fields.Monetary(store=True, string='Month value ppto')
    cop_value = fields.Monetary(store=True, string='COP value')
    currency_id = fields.Many2one(comodel_name='res.currency', store=True, readonly=True,
                                  default=lambda self: self.env.company.currency_id)

