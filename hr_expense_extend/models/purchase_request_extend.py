# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    travel_request_id = fields.Many2one(comodel_name='travel.request', string='Travel Request')
    hr_travel_info_id =  fields.Many2one(comodel_name='hr_travel_info', string='Travel Info')
    hr_hotel_info_id = fields.Many2one(comodel_name='hr_hotel_info', string='Hotel Info')
