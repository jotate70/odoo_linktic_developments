from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class HrRecruitmentRequisitionStageTransitionWizard(models.TransientModel):
    _name = 'hr_recruitment_requisition_stage_transition_wizard'
    _description = 'hr recruitment requisition Change Stage Wizard'

    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition",
                                                    string="Recruitment Requisition", ondelete='cascade')
    stage_id = fields.Many2one(comodel_name="hr_requisition_state", string="Stage")
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By',
                                 help='Jefe inmediato respondable de su aprobación')
    manager_id2 = fields.Many2one(comodel_name='hr.employee', string='Alternative Approval',
                                  help='Cuando el jefe inmediato se encuentra ausente, debe aprobar el siguiente respondable')
    manager_before = fields.Many2one(comodel_name='hr.employee', string='Approval Before')
    time_off = fields.Char(string='Disponibilidad')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')

    def do_action(self):
        if self.hr_recruitment_requisition_id:
            for rec in self.hr_recruitment_requisition_id:
                rec.button_action_on_aprobation()
                create_vals = {'hr_recruitment_requisition_id': self.hr_recruitment_requisition_id.id,
                               'stage_id': self.stage_id.id,
                               'user_id': self.manager_id.user_id.id,
                               'datetime_start': self.datetime_start,
                               'datetime_end': fields.datetime.now(),
                               'no_hours': self.no_hours,
                               'stage_result': self.stage_result,
                               }
                self.env['hr_recruitment_stage_log'].create(create_vals)



