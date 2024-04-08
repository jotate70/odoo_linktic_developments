# -*- coding: utf-8 -*-
from odoo import api, models, fields, _

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    hr_recruitment_requisition_id = fields.Many2one(comodel_name='hr_recruitment_requisition', ondelete='restrict')