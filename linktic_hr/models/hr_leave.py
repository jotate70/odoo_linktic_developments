from odoo import fields, _, models, api
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    death_certificate = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_death_certificate_rel"
                                         , column1="m2m_id", column2="attachment_id", string="Death Certificate")
    civil_registration = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_civil_registration_rel"
                                          , column1="m2m_id", column2="attachment_id", string="Civil Registration")
    is_bereavement = fields.Boolean("Is Bereavement", compute='is_a_bereavement_leave')

    @api.depends('holiday_status_id')
    def is_a_bereavement_leave(self):
        for leave in self:
            if leave.holiday_status_id == self.env.ref('linktic_hr.hr_leave_type_bereavement'):
                leave.is_bereavement = True
            else:
                leave.is_bereavement = False

    def action_approve(self):
        for record in self:
            if (not record.death_certificate or not record.civil_registration) and record.is_bereavement:
                raise UserError(_("Death Certificate and Civil Registration are mandatory for this leave"))
        return super().action_approve()
