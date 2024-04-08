# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResBankTxtConfigLine(models.Model):
    _name = 'res.bank.txt_config.line'
    _description = 'Lines of configuration of txt generator of each banks for payments in the banking portal'

    header_setting_id = fields.Many2one('res.bank.txt_config', string='Txt generator setting')
    body_setting_id = fields.Many2one('res.bank.txt_config', string='Txt generator setting')
    footer_setting_id = fields.Many2one('res.bank.txt_config', string='Txt generator setting')
    
    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    size = fields.Integer(string="Size", required=True)
    alignment = fields.Selection([('left', 'Left'), 
                                  ('right', 'Right'),],string="Alignment", required=True)
    fill = fields.Text(string="Filling", size=1, required=False)
    value_type = fields.Selection([('burned', 'Burned value'), 
                                   ('python', 'Python'),
                                   ('call', 'Call variable')], string="Value type", required=True)
    value = fields.Text(string="Value", required=True)
    
    

    
    
    
    
    
    
    
