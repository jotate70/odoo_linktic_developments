from odoo import fields, _, models, api
from odoo.exceptions import UserError


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    services_provided = fields.Boolean("Services Provided", default=False)
    project_id = fields.Many2one('project.project', string="Project")
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string="Helpdesk Ticket")

    def create_contact_from_applicant(self):
        """ Create only a contact from the hr.applicants, will be used as a vendor """
        for applicant in self:
            if not applicant.partner_name:
                raise UserError(_('You must define a Contact Name for this applicant.'))
            contact_data = {
                'default_is_company': False,
                'default_type': 'contact',
                'default_name': applicant.partner_name,
                'default_email': applicant.email_from,
                'default_phone': applicant.partner_phone,
                'default_mobile': applicant.partner_mobile,
                'form_view_initial_mode': 'edit',
                'from_recruitment_services': True,
                'applicant_id': applicant.id,
            }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('contacts.action_contacts')
        dict_act_window['views'] = [(128, 'form')]
        dict_act_window['context'] = contact_data
        return dict_act_window
