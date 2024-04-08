from odoo import fields, _, models, api
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    death_certificate = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_death_certificate_rel"
                                         , column1="m2m_id", column2="attachment_id", string="Death Certificate")
    civil_registration = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_civil_registration_rel"
                                          , column1="m2m_id", column2="attachment_id", string="Civil Registration")
    is_bereavement = fields.Boolean("Is Bereavement")
