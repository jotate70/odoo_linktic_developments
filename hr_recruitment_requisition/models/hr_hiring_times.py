# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HrHiringTimes(models.Model):
    _name = 'hr.hiring.times'
    _description = 'Hiring Times'
    _order = "sequence"

    sequence = fields.Integer(default=1)
    contract_type_id = fields.Many2one(comodel_name='hr.contract.type', string="Contract Type")
    contract_duration_qty = fields.Integer(string='Desde')
    contract_duration_qty_end = fields.Integer(string='Hasta')
    contract_duration_sel = fields.Selection(selection=[('weekly', 'Weekly'),
                                                        ('month', 'Month'),
                                                        ('annual', 'Annual'),
                                                        ('undefined', 'Undefined'),
                                                        ('project/work_duration', 'Project/Work Duration'),
                                                        ('materity_licence', 'Materity Licence'),
                                                        ('vacation_disability', 'Vacation/Disability')],
                                             string="En", default='month', required=True)