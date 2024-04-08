from odoo import models, fields, api, _
import logging

class PartnerXlsx(models.AbstractModel):
    _name = 'report.account_bank_generator.account_bank_payment_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        format1 = workbook.add_format({'font_size': 13, 'align': 'vcemter', 'bold': True})      # Header
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcemter'})      # Info
        sheet = workbook.add_worksheet('Hoja example')      # Hoja
        sheet.write(2, 2, 'contactos', format1)
        sheet.write(2, 3, 'journal_id.name', format2)
