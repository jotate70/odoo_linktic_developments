# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResBankTxtConfig(models.Model):
    _name = 'res.bank.txt_config'
    _description = 'Configuration of txt generator of each banks for payments in the banking portal'
    _rec_name = 'bank_id'

    name = fields.Char('Description')
    bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')
    header_line_id = fields.One2many(comodel_name='res.bank.txt_config.line', inverse_name='header_setting_id', string='Txt Header')
    body_line_id = fields.One2many(comodel_name='res.bank.txt_config.line', inverse_name='body_setting_id', string='Txt Body')
    footer_line_id = fields.One2many(comodel_name='res.bank.txt_config.line', inverse_name='footer_setting_id', string='Txt Footer')
    state = fields.Selection(selection=[('active', 'Active'), ('incative', 'Inactive'), ], string='State', default="active")
    file_type = fields.Selection(selection=[('txt', 'txt'), ('xlsx', 'xlsx'), ('cvs', 'cvs')],
                                 store=True, string='File Type', default='txt', required=True)
    minimum_limit_line = fields.Integer(string='Minimum Limit Line', default=1)

    @api.depends('bank_id', 'name')
    def name_get(self):
        result = []
        for txt_config in self:
            name = txt_config.bank_id.name + ' (' + str(txt_config.name or txt_config.id) + ')'
            result.append((txt_config.id, name))
        return result

    def get_txt(self, batch_payment, var_ava):
        self.ensure_one()
        txt = ''
        if not batch_payment:
            raise ValueError('There is no payment batch document to process')
        if not batch_payment.payment_ids:
            raise ValueError('There is no payment document to process')

        if self.header_line_id:
            txt += self.get_txt_line('header', batch_payment, False, var_ava)
        if self.body_line_id:
            item = 0
            for line in batch_payment.payment_ids:
                item += 1
                # Depuración de valores
                _, _, amount_dep = str(line.amount).partition(".")  # optener decimales
                beneficiary_vat = str(line.partner_id.vat).split("-")   # Optner valores antes del -
                _, _, dv_vat = str(line.partner_id.vat).partition("-")  # optener digito de verificación

                var_ava = dict(var_ava, **{
                    'item': item,
                    'beneficiary_nit': line.partner_id.l10n_latam_identification_type_id.code or '',
                    'beneficiary_vat': beneficiary_vat[0].replace("False", "") or '',   # Permite filtar
                    'beneficiary_vat_dv': dv_vat or '',
                    'payment_type': line.payment_type_id.code or '',
                    'bank_code_receiver': line.bank_id.bank_code or '',
                    'type_account': line.type_bank_account_id.code or '',
                    'beneficiary_bank': line.acc_number or '',
                    'amount_line': int(line.amount) or '',
                    'decimal_amount_line': amount_dep or '',
                    'beneficiary_name': line.partner_id.name or '',
                    'beneficiary_street': str((line.partner_id.city) or ''),
                    'beneficiary_street2': str((line.partner_id.street2) or '') + '' + str((line.partner_id.city) or ''),
                    'beneficiary_email': line.partner_id.email or '',
                })

                txt += self.get_txt_line('body', batch_payment, line, var_ava)
        if self.footer_line_id:
            txt += self.get_txt_line('footer', batch_payment, False, var_ava)

        return txt

    def get_txt_line(self, type_content, batch_payment, payment, var_ava):
        self.ensure_one()
        txt = ''
        line_fields = self.header_line_id if type_content == 'header' else \
            self.body_line_id if type_content == 'body' else \
                self.footer_line_id if type_content == 'footer' else False
        for field in line_fields.sorted(lambda s: s.sequence):
            size = field.size
            align = field.alignment
            fill = field.fill[0]
            val_type = field.value_type
            value = field.value
            txt_field = ''
            # calc val field
            if val_type == 'burned':
                txt_field += value
            elif val_type == 'python':
                txt_field = str(eval(value))
            elif val_type == 'call':
                if 'date_transmission' in value or 'date_payment' in value:
                    date, formatt = value.split(',')
                    txt_field = var_ava[date].strftime(formatt)
                elif value in var_ava:
                    txt_field = str(var_ava[value])
                else:
                    raise ValidationError(_('The value %s does not belong to one of the available variables') % value)
            # fill
            if align == 'left':
                txt_field = txt_field.ljust(size, fill)[:size]
            else:
                txt_field = txt_field.rjust(size, fill)[:size]

            txt += txt_field
        txt += '\n'
        return txt




