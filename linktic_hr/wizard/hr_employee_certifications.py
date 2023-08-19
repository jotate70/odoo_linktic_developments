# -*- coding: utf-8 -*-

from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
import os
import shutil
from zipfile import ZipFile
import base64


class HrEmployeeCertifications(models.TransientModel):
    _name = 'hr.employee.certifications.wizard'
    _description = "Employee Certifications Wizard"

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_certifications_rel', 'wizard_id', 'employee_id',
                                    string='Employees')  # , domain=_employee_ids_domain)
    addressed_to = fields.Selection(string="Addressed to",
                                    selection=[('to_whom_it_concerns', 'To Whom It Concerns'),
                                               ('addressee', 'Addressee')])
    addressee = fields.Char(string='Addressee')
    with_salary = fields.Boolean(string='Certification with salary allocation')
    own_employee = fields.Boolean(string='Is own or multiple employee')
    is_linktic = fields.Boolean(string='Is Linktic', compute='is_linktic_company')
    attachment = fields.Binary("Attachment")

    @api.model
    def default_get(self, fields_list):
        res = super(HrEmployeeCertifications, self).default_get(fields_list)
        if self._context.get('employee_user'):
            res['employee_ids'] = [(6, 0, [self.env.user.employee_id.id])]
        else:
            res['employee_ids'] = False

        res['addressed_to'] = 'to_whom_it_concerns'
        return res

    def is_linktic_company(self):
        for record in self:
            record.is_linktic = self.env.company.id == 1

    @api.onchange('employee_ids')
    def add_inactive_to_employees(self):
        return {'domain': {'employee_ids': [('active', 'in', [True, False])]}}

    def generate_certificates(self):
        if len(self.employee_ids) == 1:
            data = {
                'employee_id': self.employee_ids.id,
                'employee_name': self.employee_ids.display_name,
                'employee_id_number': self.employee_ids.identification_id,
                'employee_expedition_place': self.employee_ids.expedition_place_id,
                'active_employee': _('currently works') if self.employee_ids.active else _('worked'),
                'active_employee_2': _('has been performing') if self.employee_ids.active else _('performed'),
                'h3_string': self.addressee if self.addressed_to == 'addressee' else dict(
                    self._fields['addressed_to']._description_selection(self.env)).get(self.addressed_to),
                'addressed_to': self.addressed_to,
                'addressee': self.addressee,
                'with_salary': self.with_salary,
                'is_linktic': self.employee_ids.company_id.id == 1,
            }
            return self.sudo().env.ref('linktic_hr.action_employee_certificate_pdf_report').report_action(self,
                                                                                                          data=data)

        elif len(self.employee_ids) > 1:
            certificates = []
            for employee in self.employee_ids:
                data = {
                    'employee_id': employee.id,
                    'employee_name': employee.display_name,
                    'employee_id_number': employee.identification_id,
                    'employee_expedition_place': employee.expedition_place_id,
                    'active_employee': _('currently works') if employee.active else _('worked'),
                    # 'active_employee_2': _('has been performing') if self.employee_ids.active else _('performed'),
                    'active_employee_2': _('has been performing') if self.employee_ids.ids else _('performed'),
                    'h3_string': self.addressee if self.addressed_to == 'addressee' else dict(
                        self._fields['addressed_to']._description_selection(self.env)).get(self.addressed_to),
                    'addressed_to': self.addressed_to,
                    'addressee': self.addressee,
                    'with_salary': self.with_salary,
                    'is_linktic': employee.company_id.id == 1,
                }
                report_pdf, r_type = self.env.ref('linktic_hr.action_employee_certificate_pdf_report')._render_qweb_pdf(
                    self, data=data)
                certificates.append((employee.display_name, report_pdf))

            path = '/tmp' + '/' + str('Employee_certificates')
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)
            zipfilepath = os.path.join(path, 'Certificates.zip')
            zip_object = ZipFile(zipfilepath, 'w')
            file_name = _('Certificates')

            if certificates:
                for record in certificates:
                    object_name = path + '/' + record[0]
                    try:
                        with open(object_name, "wb") as attach:
                            attach.write(record[1])
                        try:
                            zip_object.write(object_name, record[0] + '.pdf')
                        except ValueError:
                            pass
                    except FileNotFoundError:
                        pass
                zip_object.close()

                with open(zipfilepath, "rb") as file:
                    file_base64 = base64.b64encode(file.read())
                self.write({'attachment': file_base64})

                return {
                    'close_on_report_download': True,
                    'type': 'ir.actions.act_url',
                    'name': ('%s.zip', file_name),
                    'url': '/web/content/hr.employee.certifications.wizard/%s/attachment/%s.zip?download=true' % (
                        self.id, file_name),
                }


class EmployeeCertificateReportPDF(models.AbstractModel):
    _name = 'report.linktic_hr.employee_certification_pdf_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        # domain = [('state', '!=', 'cancel')]
        domain = []
        if data.get('employee_id'):
            domain.append(('employee_id', '=', data.get('employee_id')))
        employees = self.env['hr.employee'].browse(data.get('employee_id'))
        employee_contracts = self.env['hr.contract'].search(domain)
        # learning_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id == 15)
        # services_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id in (12, 13, 14, 16, 17))
        # payroll_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id in (10, 11))
        # /////////////////////////////////////   NEW CODE ///////////////////////////////////////////////////
        apprenticeship_type_contract_id = self.env['hr.contract.type'].search(
            [('contract_type_id', '=', 'apprenticeship_type_contract')])
        temporary_type_contract_id = self.env['hr.contract.type'].search(
            [('contract_type_id', '=', 'temporary_type_contract')])
        undefined_contract_type_id = self.env['hr.contract.type'].search(
            [('contract_type_id', '=', 'undefined_contract_type')])
        learning_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id == apprenticeship_type_contract_id.ids)
        services_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id in temporary_type_contract_id.ids)
        payroll_contracts = employee_contracts.filtered(lambda c: c.contract_type_id.id in undefined_contract_type_id.ids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.contract',
            'employees': employees,
            'contracts': employee_contracts,
            'learning_contracts': learning_contracts,
            'no_learning_contracts': len(learning_contracts),
            'services_contracts': services_contracts,
            'no_services_contracts': len(services_contracts),
            'payroll_contracts': payroll_contracts,
            'no_payroll_contracts': len(payroll_contracts),
            'datas': data,
        }
