from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _get_eps_domain(self):
        return [('category_id', 'in', [self.env.ref('linktic_hr.res_partner_cat_eps').id])]

    @api.model
    def _get_arl_domain(self):
        return [('category_id', 'in', [self.env.ref('linktic_hr.res_partner_cat_arl').id])]

    @api.model
    def _get_layoffs_domain(self):
        return [('category_id', 'in', [self.env.ref('linktic_hr.res_partner_cat_layoffs').id])]

    @api.model
    def _get_pension_domain(self):
        return [('category_id', 'in', [self.env.ref('linktic_hr.res_partner_cat_pension').id])]

    expedition_place_id = fields.Char(string='Expedition Place', groups="hr_attendance.group_hr_attendance_kiosk")
    age = fields.Integer(string="Age", compute="compute_employee_age")
    rh = fields.Selection(
        selection=[('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'),
                   ('o-', 'O-')]
        , string="RH", groups="hr.group_hr_user")
    seniority = fields.Selection(
        selection=[('expert', 'Expert'), ('senior', 'Senior'), ('semisenior', 'Semi-senior'), ('junior', 'Junior'),
                   ('trainee', 'Trainee'), ('professional', 'Professional'), ('analyst', 'Analyst'),
                   ('assistant', 'Assistant')]
        , string="Seniority", groups="hr.group_hr_user")
    eps = fields.Many2one('res.partner', 'EPS', groups="hr.group_hr_user", tracking=True, domain=_get_eps_domain)
    arl = fields.Many2one('res.partner', 'ARL', groups="hr.group_hr_user", tracking=True, domain=_get_arl_domain)
    layoffs = fields.Many2one('res.partner', 'Layoffs', groups="hr.group_hr_user", tracking=True,
                              domain=_get_layoffs_domain)
    pension = fields.Many2one('res.partner', 'Pension', groups="hr.group_hr_user", tracking=True,
                              domain=_get_pension_domain)
    worked_months = fields.Integer(string="Worked Months", compute="compute_worked_months", groups="hr.group_hr_user")
    entrance_ticket = fields.Char("Entrance Ticket")
    applied_computer = fields.Boolean("Applied Computer", default=False)
    observations = fields.Text("Observations")
    contact_neighborhood = fields.Char("Neighborhood", related='address_home_id.neighborhood')
    contact_locality = fields.Char('Locality', related='address_home_id.locality')
    contract_wage = fields.Monetary('Contract Wage', related='contract_id.wage')
    contract_welfare_aid = fields.Monetary('Welfare Assistance', related='contract_id.welfare_aid')
    contract_food_aid = fields.Monetary('Food Assistance', related='contract_id.food_aid')
    contract_transport_aid = fields.Monetary('Transport Assistance', related='contract_id.transport_aid')
    contract_bearing_aid = fields.Monetary('Bearing Assistance', related='contract_id.bearing_aid')
    contract_total_income = fields.Monetary('Total Income', related='contract_id.total_income')
    contract_type_id = fields.Many2one('hr.contract.type', "Contract Type", related='contract_id.contract_type_id')
    contract_analytic_account_id = fields.Many2one('account.analytic.account', 'Contract Analytic Account',
                                                   related='contract_id.analytic_account_id')
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type',
                                                        string="Identification Type", index=True, auto_join=True,
                                                        default=lambda self: self.env.ref('l10n_latam_base.it_vat',
                                                                                          raise_if_not_found=False),
                                                        help="The type of identification")
    seniority = fields.Selection(
        selection=[('expert', 'Expert'), ('senior', 'Senior'), ('semisenior', 'Semi-senior'), ('junior', 'Junior'),
                   ('trainee', 'Trainee'), ('professional', 'Professional'), ('analyst', 'Analyst'),
                   ('assistant', 'Assistant')]
        , string="Seniority", groups="hr.group_hr_user")
    arl_risk_id = fields.Many2one('hr.employee.arl.risk', string='Risk Level')
    arl_contribution_percentage = fields.Float('Contribution %', related='arl_risk_id.contribution_percentage')
    recruitment_degree_id = fields.Many2one('hr.recruitment.degree', string="Grade")
    emergency_kinship = fields.Char(string="Contact Relationship")
    first_name = fields.Char(string="First Name")
    second_name = fields.Char(string="Second Name")
    first_last_name = fields.Char(string="First Last Name")
    second_last_name = fields.Char(string="Second Last Name")
    contact_address = fields.Char(string="Address", help="field used to save the contact address field",
                                  related="address_home_id.street")
    contact_address2 = fields.Char(string="Address Complement",
                                   help="field used to save the contact address complement field",
                                   related="address_home_id.street2")
    contact_city = fields.Char(string="City of Residence", help="field used to save the contact city field",
                               related="address_home_id.city")
    curriculum_vitae_url = fields.Char(string="Curriculum Vitae URL")
    business_photo_url = fields.Char(string="Business Photo URL")
    contact_bank_number = fields.Char(string="Bank Account", compute="get_contact_bank_account")
    contact_bank_name = fields.Char(string="Bank Name", compute="get_contact_bank_account")
    category_ids_labels = fields.Char(string="Category Labels", compute="get_employee_category_labels")
    gender_value = fields.Char(string="Gender Value", compute="get_gender_value")
    active_value = fields.Char(string="Active Value", compute="get_active_value")

    # Fields to parse dates to dd/mm/aaaa
    label_birthday = fields.Char('Label Birthday', compute='get_spreadsheet_integration_dates')
    label_first_contract_date = fields.Char('Label First Contract Date', compute='get_spreadsheet_integration_dates')
    label_departure_date = fields.Char('Label Departure Date', compute='get_spreadsheet_integration_dates')

    # Fields changed to let all the employees create their certificate
    identification_id = fields.Char(groups="hr_attendance.group_hr_attendance_kiosk")

    # Fields New
    hhrr_manager_id = fields.Many2one(comodel_name='hr.employee', string='HHRR Manager')

    def get_spreadsheet_integration_dates(self):
        for employee in self:
            employee.label_birthday = employee.birthday.strftime("%d/%m/%Y") if employee.birthday else False
            employee.label_first_contract_date = employee.first_contract_date.strftime(
                "%d/%m/%Y") if employee.first_contract_date else False
            employee.label_departure_date = employee.departure_date.strftime(
                "%d/%m/%Y") if employee.departure_date else False

    def get_active_value(self):
        for record in self:
            record.active_value = 'ACTIVO' if record.active else 'RETIRADO'

    def get_gender_value(self):
        for record in self:
            if record.gender:
                record.gender_value = 'MASCULINO' if record.gender == 'male' else 'FEMENINO'
            else:
                record.gender_value = False

    @api.onchange('first_name', 'first_last_name', 'second_name', 'second_last_name')
    def get_name_from_parts(self):
        for record in self:
            record.name = f"{record.first_name}{' ' + record.second_name if record.second_name else ''}{' ' + record.first_last_name if record.first_last_name else ''}{' ' + record.second_last_name if record.second_last_name else ''}"

    def get_employee_category_labels(self):
        for record in self:
            record.category_ids_labels = ','.join(record.category_ids.mapped('name'))

    def get_contact_bank_account(self):
        for record in self:
            if record.address_home_id.bank_ids:
                record.contact_bank_number = record.address_home_id.bank_ids[0].acc_number
                record.contact_bank_name = record.address_home_id.bank_ids[0].bank_name
            else:
                record.contact_bank_number = False
                record.contact_bank_name = False

    def compute_employee_age(self):
        for record in self:
            if record.birthday:
                record.age = relativedelta(fields.Datetime.now(), record.birthday).years
            else:
                record.age = False

    def compute_worked_months(self):
        for record in self:
            if record.first_contract_date:
                record.worked_months = relativedelta(fields.Datetime.now(), record.first_contract_date).months
            else:
                record.worked_months = False

    @api.onchange('job_id')
    def update_job_title(self):
        for record in self:
            if record.job_id:
                record.job_title = record.job_id.name


class HrEmployeeArlRisk(models.Model):
    _name = "hr.employee.arl.risk"
    _description = "HR Employee ARL Risk"

    name = fields.Char('Name')
    contribution_percentage = fields.Float(string="Contribution %")
