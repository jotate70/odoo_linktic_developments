from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HelpdeskTicketStageTransitionWizard(models.TransientModel):
    _name = 'helpdesk.ticket.stage.transition.wizard'
    _description = 'Helpdesk Ticket Change Stage Wizard'

    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket', required=True)
    stage_sequence = fields.Integer(string='Stage Sequence')
    ticket_actual_stage_id = fields.Many2one('helpdesk.ticket.stage', related='helpdesk_ticket_id.stage_id')
    valid_ticket_stage_ids = fields.Many2many('helpdesk.ticket.stage', 'ticket_transit_wizard_cat_rel', 'ticket_id',
                                              'cat_id', string='Valid Stages')
    next_stage_id = fields.Many2one('helpdesk.ticket.stage', string='Next Stage',
                                    domain="[('id', 'in', valid_ticket_stage_ids)]")
    stage_result = fields.Text(string='Stage Results')

    def do_action(self):
        self.ensure_one()

        last_change = self.env['helpdesk.ticket.stage.log'].search(
            [('helpdesk_ticket_id', '=', self.helpdesk_ticket_id.id), ('datetime_start', '!=', False)],
            order='datetime_start desc', limit=1)
        if last_change:
            working_calendar = self.helpdesk_ticket_id.team_id.resource_calendar_id
            calculated_hours = working_calendar.get_work_hours_count(last_change.datetime_start
                                                                     , datetime.now()
                                                                     , compute_leaves=True)
            last_change.current_log = False
            last_change.update({'current_log': False, 'no_hours': calculated_hours, 'stage_result': self.stage_result})
        vals_log = {'helpdesk_ticket_id': self.helpdesk_ticket_id.id, 'stage_id': self.next_stage_id.id,
                    'datetime_start': datetime.now(), 'user_id': self.env.user.id,
                    'current_log': True}
        self.env['helpdesk.ticket.stage.log'].create(vals_log)

        self.helpdesk_ticket_id.update(
            {'stage_id': self.next_stage_id, 'stage_sequence': self.helpdesk_ticket_id.stage_sequence + 1,
             'stage_approve': False})
