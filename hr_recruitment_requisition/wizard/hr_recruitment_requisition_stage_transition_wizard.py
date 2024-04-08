from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json

class HrRecruitmentRequisitionStageTransitionWizard(models.TransientModel):
    _name = 'hr_recruitment_requisition_stage_transition_wizard'
    _description = 'hr recruitment requisition Change Stage Wizard'

    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition",
                                                    string="Recruitment Requisition", ondelete='cascade')
    state_domain = fields.Char(string='State Domain', compute='_compute_state_domain')
    stage_id = fields.Many2one(comodel_name="hr_requisition_state", string="Stage")
    approved_by = fields.Many2one(comodel_name='res.users', string='Approved By',
                                  default=lambda self: self.env.user)
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By',
                                 help='Jefe inmediato respondable de su aprobación')
    manager_after_id = fields.Many2one(comodel_name='hr.employee', string='Manager next stage',
                                 help='Jefe inmediato respondable de su aprobación')
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval')
    recruitment_type_id = fields.Many2one(comodel_name='hr_recruitment_type', string='Recruitment Type')
    time_off = fields.Char(string='Disponibilidad')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')
    button_cancel = fields.Boolean(string='Button cancel')

    def do_action(self):
        if self.hr_recruitment_requisition_id:
            for rec in self.hr_recruitment_requisition_id:
                create_vals = {'hr_recruitment_requisition_id': self.hr_recruitment_requisition_id.id,
                               'stage_id': self.stage_id.id,
                               'user_id': self.approved_by.id,
                               'datetime_start': self.datetime_start,
                               'datetime_end': fields.datetime.now(),
                               'no_hours': self.no_hours,
                               'stage_result': self.stage_result,
                               }
                self.env['hr_recruitment_stage_log'].create(create_vals)
                employee = self.env['hr_recruitment_requisition'].search([('id','=',self.hr_recruitment_requisition_id.ids)], limit=1)
                employee.write({'manager_after_id': self.manager_after_id.id})

                # Apply changes in contract
                if rec.state.apply_contract_changes:
                    rec.action_process()

                rec.compute_next_stage2()

    def do_action_cancel(self):
        if self.hr_recruitment_requisition_id:
            for rec in self.hr_recruitment_requisition_id:
                create_vals = {'hr_recruitment_requisition_id': self.hr_recruitment_requisition_id.id,
                               'stage_id': self.stage_id.id,
                               'user_id': self.approved_by.id,
                               'datetime_start': self.datetime_start,
                               'datetime_end': fields.datetime.now(),
                               'no_hours': self.no_hours,
                               'stage_result': self.stage_result,
                               }
                self.env['hr_recruitment_stage_log'].create(create_vals)
                rec.button_action_cancel()

    # function domain dynamic
    @api.depends('recruitment_type_id')
    def _compute_state_domain(self):
        for rec in self:
            if rec.recruitment_type_id:
                rec.state_domain = json.dumps([('id', 'in', rec.recruitment_type_id.state_id.ids)])
            else:
                rec.state_domain = json.dumps([()])



