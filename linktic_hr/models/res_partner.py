from odoo import fields, _, models, api


class Partner(models.Model):
    _inherit = "res.partner"

    neighborhood = fields.Char("Neighborhood")
    locality = fields.Char('Locality')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        is_from_applicant = self.env.context.get('from_recruitment_services')
        if is_from_applicant:
            applicant_obj = self.env['hr.applicant'].browse(self.env.context.get('applicant_id'))
            applicant_obj.partner_id = res.id
        return res
