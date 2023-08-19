from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

compare_fields = ['wizard_updated_job', 'wizard_updated_contract_type_id', 'wizard_updated_contract_date_end',
                  'wizard_contract_wage_rise']


class HelpdeskUpdateContractInfoWizard(models.TransientModel):
    _name = 'helpdesk.update.contract.info.wizard'
    _description = 'Helpdesk Update Contract Info Wizard'

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket', required=True)
    wizard_updated_job = fields.Char(string='New Job Position')
    wizard_updated_contract_type_id = fields.Many2one('hr.contract.type', string="New Contract Type")
    wizard_updated_contract_date_end = fields.Date(string='New Contract End Date')
    wizard_contract_wage_rise = fields.Monetary('Contract Wage Rise')
    currency_id = fields.Many2one(string="Currency", related='helpdesk_ticket_id.company_id.currency_id')

    def do_action(self):
        self.ensure_one()
        update_vals = {}

        for field in compare_fields:
            if eval('self.' + field + ' != self.helpdesk_ticket_id.' + field.replace('wizard_', '')):
                if self._fields.get(field).type == 'many2one':
                    value = eval('self.' + field + '.id')
                elif self._fields.get(field).type == 'many2many':
                    value = eval('[(6, 0, self.' + field + '.ids)]')
                else:
                    value = eval('self.' + field)

                update_vals[field.replace('wizard_', '')] = value

        if update_vals:
            for key, value in update_vals.items():
                if self.helpdesk_ticket_id._fields.get(key).type == 'many2one':
                    ori_value = eval('self.helpdesk_ticket_id.' + key + '.name') or ''
                    new_value = eval('self.wizard_' + key + '.name') or ''
                else:
                    ori_value = eval('self.helpdesk_ticket_id.' + key) or ''
                    new_value = value

                log_vals = {'helpdesk_ticket_id': self.helpdesk_ticket_id.id,
                            'stage_id': self.helpdesk_ticket_id.stage_id.id,
                            'user_id': self.env.user.id,
                            'change_datetime': datetime.now(),
                            'field_name': self.env['ir.translation'].get_field_string(self.helpdesk_ticket_id._name)[key],
                            'origin_value': ori_value,
                            'actual_value': new_value,
                            }

                self.env['helpdesk.contract.info.log'].create(log_vals)

            self.helpdesk_ticket_id.update(update_vals)
