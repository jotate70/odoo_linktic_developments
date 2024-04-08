from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    is_vacation = fields.Boolean(string="Is Vacation")
    dominican_discount = fields.Boolean(string="Dominican Discount")
