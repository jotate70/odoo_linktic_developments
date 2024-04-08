# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractManagementClassSetting(models.Model):
    _name = 'contract.management.class.setting'
    _description = 'Change management Class settings for contracts'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code", required=True, copy=False)
    field_id = fields.Many2one(
        "ir.model.fields", string="Field", required=True, copy=False,
        domain="[('model_id.model', '=', 'hr.contract'), ('store', '=', True),"
               "('compute', '=', False), ('related', '=', False)]", ondelete='cascade', index=True)
    relation_field_id = fields.Many2one("ir.model.fields", related="field_id.related_field_id")


class ContractManagementReasonSetting(models.Model):
    _name = 'contract.management.reason.setting'
    _description = 'Change management reason settings for contracts'

    name = fields.Char(string="Name", required=True, copy=False)
    class_ids = fields.Many2many("contract.management.class.setting", "reason_id_class_id_rel", "reason_id", "class_id",
                                 string="Class", copy=True)
