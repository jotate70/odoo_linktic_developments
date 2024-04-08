from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    document_repository = fields.Char(string="Documents Repository")
    converted_to_attachments = fields.Boolean(string="Converted to Attachments")

    def convert_drive_files_to_attachment(self):
        valid_records = self.env['hr.employee'].search(
            [('document_repository', '!=', False), ('converted_to_attachments', '=', False)])

        for record in valid_records:
            google_drive_obj = self.env['linktic.google.drive.config']
            drive_service = google_drive_obj.set_google_drive_service()
            google_drive_obj.convert_drive_files_to_attachments(drive_service=drive_service, model='hr.employee',
                                                                res_id=record.id)
