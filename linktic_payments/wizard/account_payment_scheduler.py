# -*- coding: utf-8 -*-

from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _name = 'account.payment.scheduler'
    _description = 'Scheduler for bill payments'

    active_move_ids = fields.Many2many(string="Moves", comodel_name='account.move', required=True)
    company_id = fields.Many2many(string="company", comodel_name='res.company', required=True)
    scheduled_payment_day = fields.Date(string='Scheduled Payment Date', required=True)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Bank',
                                         domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")

    def action_schedule_payments(self):
        self.active_move_ids.scheduled_payment_day = self.scheduled_payment_day
        self.active_move_ids.payment_journal_id = self.payment_journal_id
