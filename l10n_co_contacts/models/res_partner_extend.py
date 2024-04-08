# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class l10n_co_contacts(models.Model):
    _inherit = 'res.partner'

    # campos relacionados de ajustes
    check_vat = fields.Boolean(string='Vat', compute='get_partner')
    check_phone = fields.Boolean(string='Teléfono', compute='get_partner')
    check_mobile = fields.Boolean(string='Móvil', compute='get_partner')
    check_email = fields.Boolean(string='Correo electrónico', compute='get_partner')
    check_website = fields.Boolean(string='Sitio web', compute='get_partner')

    # Función que llaman los valores en modelo settings
    def get_partner(self):
        for record in self:
            record.check_vat = record.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_vat')
            record.check_phone = record.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_phone')
            record.check_mobile = record.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_mobile')
            record.check_email = record.env['ir.config_parameter'].sudo().get_param('l10n_co_contacts_constraint.check_email')
            record.check_website = record.env['ir.config_parameter'].sudo().get_param(
                'l10n_co_contacts_constraint.check_website')
            return record.check_vat, record.check_phone, record.check_mobile, record.check_email, record.check_website

    # Borrar campos de contacto cuando se deseleciona una compañia en un individual
    @api.onchange('parent_id')
    def _clean_contact_parent(self):
        for record in self:
            if record.is_company == False:
                record.write({'street': False})
                record.write({'street2': False})
                record.write({'city': False})
                record.write({'state_id': False})
                record.write({'zip': False})
                record.write({'vat': False})

    # No duplicar número de identificación
    @api.constrains('vat')
    def _constraint_vat(self):
        for rec in self:
            partners = rec.search([('vat', '=', rec.vat)])
            longitud = len(partners)
            if rec.vat == False:
                longitud = 0
            if rec.is_company == True:
                if longitud > 1 and rec.check_vat == True:
                    raise exceptions.ValidationError('El número de identificación ya existe')
            else:
                if rec.commercial_partner_id != rec.parent_id:
                    if longitud > 1 and rec.check_vat == True:
                        raise exceptions.ValidationError('El número de identificación ya existe')

    # No duplicar teléfono
    @api.constrains('phone')
    def _constraint_phone(self):
        for record in self:
            partners = record.search([('phone', '=', record.phone)])
            longitud = len(partners)
            if longitud > 1 and record.check_phone == True:
                raise exceptions.ValidationError('El teléfono ya existe')

    # No duplicar número móvil
    @api.constrains('mobile')
    def _constraint_mobile(self):
        for record in self:
            partners = record.search([('mobile', '=', record.mobile)])
            longitud = len(partners)
            if longitud > 1 and record.check_mobile == True:
                raise exceptions.ValidationError('El número móvil ya existe')

    # No duplicar correo electrónico
    @api.constrains('email')
    def _constraint_email(self):
        for record in self:
            partners = record.search([('email', '=', record.email)])
            longitud = len(partners)
            if longitud > 1 and record.check_email == True:
                raise exceptions.ValidationError('El correo electrónico ya existe')

    # No duplicar sitio web
    @api.constrains('website')
    def _constraint_website(self):
        for record in self:
            partners = record.search([('website', '=', record.website)])
            longitud = len(partners)
            if longitud > 1 and record.check_website == True:
                raise exceptions.ValidationError('El sitio web ya existe')
