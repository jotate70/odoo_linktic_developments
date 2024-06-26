from odoo import api, fields, models, _
import json

class HrApplicantStageTransitionWizard(models.TransientModel):
    _name = 'hr_applicant_stage_transition_wizard'
    _description = 'hr applicant Change Stage Wizard'

    recruitment_type_id = fields.Many2many(comodel_name='hr_recruitment_type',
                                           help='Match the stages with the types of personnel request.')
    hr_applicant_id = fields.Many2one(comodel_name="hr.applicant",
                                       string="Applicant", ondelete='cascade')
    hr_recruitment_requisition_id = fields.Many2one(comodel_name="hr_recruitment_requisition",
                                                    string="Recruitment Requisition", ondelete='cascade')
    stage_domain = fields.Char(string='State Domain', compute='_compute_stage_domain')
    stage_id = fields.Many2one(comodel_name="hr.recruitment.stage", string="Stage")
    approved_by = fields.Many2one(comodel_name='res.users', string='Approved By',
                                  default=lambda self: self.env.user)
    manager_id = fields.Many2one(comodel_name='hr.employee', string='Approve By',
                                 help='Jefe inmediato respondable de su aprobación')
    manager_after_id = fields.Many2one(comodel_name='hr.employee', string='Manager next stage',
                                       help='Jefe inmediato respondable de su aprobación')
    requires_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Requires Approval')
    time_off = fields.Char(string='Disponibilidad')
    time_off_related = fields.Boolean(string='Ausencia', related='manager_id.is_absent')
    datetime_start = fields.Datetime(string='Start Date')
    datetime_end = fields.Datetime(string='End Date')
    no_hours = fields.Float(string='No. Hours')
    stage_result = fields.Text(string='Stage Results')

    def do_action(self):
        if self.hr_applicant_id:
            for rec in self.hr_applicant_id:
                create_vals = {'hr_applicant_id': rec.id,
                               'hr_recruitment_requisition_id': self.hr_recruitment_requisition_id.id,
                               'stage_id': self.stage_id.id,
                               'user_id': self.approved_by.id,
                               'datetime_start': self.datetime_start,
                               'datetime_end': fields.datetime.now(),
                               'no_hours': self.no_hours,
                               'stage_result': self.stage_result,
                               }
                self.env['hr_applicant_stage_log'].create(create_vals)
                employee = self.env['hr.applicant'].search([('id', '=', self.hr_applicant_id.ids)], limit=1)
                employee.write({'manager_after_id': self.manager_after_id.id})
                # Movimiento de etapas
                rec.compute_next_stage()
                if self.hr_applicant_id.stage_after.hired_stage == True:
                    create_vals2 = {'hr_recruitment_requisition_id': self.hr_recruitment_requisition_id.id,
                                    'stage_id': self.hr_recruitment_requisition_id.state.id,
                                    'user_id': self.approved_by.id,
                                    'datetime_start': self.hr_recruitment_requisition_id.write_date,
                                    'datetime_end': fields.datetime.now(),
                                    'no_hours': self.no_hours,
                                    'stage_result': self.stage_result,
                                    }
                    self.env['hr_recruitment_stage_log'].create(create_vals2)


    # function domain dynamic
    @api.depends('recruitment_type_id')
    def _compute_stage_domain(self):
        for rec in self:
            if rec.recruitment_type_id:
                rec.stage_domain = json.dumps([('id', 'in', rec.recruitment_type_id.stage_id.ids)])
            else:
                rec.stage_domain = json.dumps([()])



