# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from datetime import datetime
from pytz import timezone

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json


class AccountBatchPayment(models.Model):
    _name = 'account.batch.payment'
    _inherit = ['account.batch.payment', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']

    state = fields.Selection(selection=[('draft', 'New'),
                                        ('sent', 'Sent'),
                                        ('reconciled', 'Reconciled')],
                             readonly=True, default='draft',
                             copy=False, traking=True, track_visibility='onchange')
    payment_type_domain = fields.Char(string='Domain type payment', compute='_compute_payment_type_domain')
    payment_type_id = fields.Many2one(comodel_name='payment.type', string="Payment type", domain='payment_type_domain')
    txt_filename = fields.Char(string="Name file")
    txt_file = fields.Binary(string="Generated file")
    minimum_limit_line = fields.Integer(string='Minimum Limit Line')

    # function domain dynamic
    @api.depends('journal_id')
    def _compute_payment_type_domain(self):
        for rec in self:
            if rec.journal_id:
                vat = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False), ('bank_id', '=', self.journal_id.bank_id.id)])
                rec.payment_type_domain = json.dumps([('id', 'in', vat.ids)])
            else:
                rec.payment_type_domain = json.dumps([])

    #def action_validate_batch_button(self):
    #    res = super(AccountBatchPayment, self).action_validate_batch_button()
    #    for rec in self.payment_ids:
    #        vat = len(rec)
    #    if vat >= self.minimum_limit_line:
    #        raise ValidationError(_('does not meet the minimum number of lines to generate a batch payment file for the selected bank.'))
    #    return res

    def _get_payment_type(self):
        if self.journal_id and self.journal_id.bank_id:
            payment_type_ids = self.env['payment.type'].search(
                [('active', '=', True), '|', ('bank_id', '=', False), ('bank_id', '=', self.journal_id.bank_id.id)]).ids
        else:
            payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids
        return [('id', 'in', payment_type_ids)]

    @api.depends('journal_id')
    def _get_employee_depends(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.bank_id:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False),
                                                                    ('bank_id', '=', rec.journal_id.bank_id.id)]).ids
            else:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids

            return {'domain': {'payment_type_id': [('id', 'in', payment_type_ids)]}}

    @api.onchange('journal_id')
    def _get_employee_onchange(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.bank_id:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False),
                                                                    ('bank_id', '=', rec.journal_id.bank_id.id)]).ids
            else:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids

            return {'domain': {'payment_type_id': [('id', 'in', payment_type_ids)]}}

    @api.onchange('payment_type_id')
    def _compute_payment_type_id(self):
        for rec in self.payment_ids:
            rec._compute_payment_type_id()
            self.minimum_limit_line = self.env['res.bank.txt_config'].search(
                [('bank_id', 'in', self.journal_id.bank_id.ids),
                 ('state', '=', 'active')], limit=1).minimum_limit_line

    def generate_txt(self):
        txt_setting_obg = self.env['res.bank.txt_config']
        for record in self:
            bank_id = record.journal_id.bank_id or False
            if not bank_id:
                raise ValidationError(_('Bank not found'))
            txt_setting_id = txt_setting_obg.search([('bank_id', '=', bank_id.id), ('state', '=', 'active')], limit=1)
            if not txt_setting_id:
                raise ValidationError(_('No txt configuration record found for bank %s') % bank_id.name)
            txt = txt_setting_id.get_txt(record)
            date_txt = datetime.now(timezone(self.env.user.tz or 'GTM'))
            record.txt_filename = 'PAGO_' + record.name + '_' + bank_id.name + '_' + date_txt.strftime(
                '%d-%m-%Y %H:%M:%S') + '.txt'
            record.txt_file = b64encode(txt.encode('utf-8')).decode('utf-8', 'ignore')

    #def generate_cvs(self):
    #    data = []
    #    for rec in self.payment_ids:
    #        data.append([rec.name, rec.date])
    #    arr = numpy.asarray(data)
    #    numpy.savetxt('C:\Users\jotat\Downloads', arr, delimiter=";", newline="\n", fmt="%s")



