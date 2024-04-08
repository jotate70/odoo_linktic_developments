# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from datetime import datetime
from pytz import timezone

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PaymentTxtGeneratorWizard(models.TransientModel):
    _name = 'payment.txt.generator.wizard'
    _description = 'Txt generator'

    def _get_txt_setting_ids(self):
        txt_setting_ids = []
        batch_id = False

        if self.env.context.get('active_model') == 'account.batch.payment':
            batch_id = self.env.context.get('active_id')
            batch_id = self.env['account.batch.payment'].search([('id', '=', batch_id)])

        if batch_id and batch_id.journal_id.bank_id:
            txt_setting_obg = self.env['res.bank.txt_config']
            txt_setting_ids = txt_setting_obg.search([('bank_id','=', batch_id.journal_id.bank_id.id), ('state', '=', 'active')]).ids

        return [('id', 'in', txt_setting_ids)]

    batch_payment_id = fields.Many2one(comodel_name='account.batch.payment')
    transmission_date = fields.Datetime(string="Transmission date", default=fields.Datetime.now)
    txt_setting_id = fields.Many2one(comodel_name='res.bank.txt_config', string='File Config', domain=_get_txt_setting_ids)


    def generate_txt(self):
        self.ensure_one()
        txt_setting_obg = self.env['res.bank.txt_config']
        batch_payment_obj = self.env[self._context.get('active_model')]
        batch_id = batch_payment_obj.browse(self._context.get('active_id')) or False
        if not batch_id:
            raise ValidationError(_('The system does not detect the payment batch record to generate the txt file'))

        bank_id = batch_id.journal_id.bank_id or False
        if not bank_id:
            raise ValidationError(_('Bank not found'))

        if self.txt_setting_id:
            txt_setting_id = self.txt_setting_id
        else:
            txt_setting_id = txt_setting_obg.search([('bank_id','=',bank_id.id),('state','=','active')], limit=1)

        if not txt_setting_id:
            raise ValidationError(_('No txt configuration record found for bank %s') % bank_id.name)

        var_ava = self.get_var_ava(batch_id)
        txt = txt_setting_id.get_txt(batch_id, var_ava)

        batch_id.txt_filename = 'PAGO_' + \
                                batch_id.name + \
                                '_' + \
                                bank_id.name + \
                                '_' + \
                                var_ava['date_transmission'].strftime('%d-%m-%Y %H:%M:%S') + \
                                '.txt'
        batch_id.txt_file = b64encode(txt.encode('utf-8')).decode('utf-8', 'ignore')

    def get_var_ava(self, batch_payment):
        return {
            'company_name': batch_payment.journal_id.company_id.name,
            'company_nit': batch_payment.journal_id.company_id.partner_id.l10n_latam_identification_type_id.code or '',
            'company_vat': batch_payment.journal_id.company_id.partner_id.vat or '',
            'company_bank_account': batch_payment.journal_id.bank_account_id.acc_number,
            'company_street': batch_payment.journal_id.company_id.partner_id.street,
            'date_payment': batch_payment.date,
            'date_transmission': self.transmission_date.astimezone(timezone(self.env.user.tz)),
            'amount_total': sum([int(x.amount_signed) for x in batch_payment.payment_ids]),
            'number_lines': len(batch_payment.payment_ids),
            'bank_acc_number': batch_payment.journal_id.bank_acc_number,
            'vat': batch_payment.journal_id.company_id.vat,
            'payment_type': batch_payment.payment_type_id.code,
            'payment_type_name': batch_payment.payment_type_id.name,
            'concept1': batch_payment.description or '',
            'concept2': '',
        }    


