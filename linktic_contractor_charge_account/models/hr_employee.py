from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    address_home_id = fields.Many2one(groups="base.group_user")
