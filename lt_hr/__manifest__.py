# Autor: Diego Torres
# Desarrollador y Consultor Odoo
# Linkedln: https://www.linkedin.com/in/diego-felipe-torres-reyes-083091152/
# Email: 20diegotorres01@gmail.com
# Github: DiTo1005
# Cel. +57 3108804090

{
    'name': 'Modificaciones Talento Humano - LinkTic SAS',
    'icon': '/lt_hr/static/description/icon.png',
    'version': '1.0',
    'summary': 'Modificaciones en el proceso talento humano de LinkTic SAS',
    'description': """
        Este módulo realiza cambios en el proceso y campos del proceso de talento humano para la empresa LinkTic SAS.
    """,
    'author': 'Diego Felipe Torres Reyes',
    'license': 'AGPL-3',
    'website': 'https://www.linktic.com',
    'category': 'Human Resources',
    'depends': ['base', 'hr', 'linktic_hr', 'l10n_co_hr_payroll', 'account'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security.xml',
        # Views
        'views/hr_department_views.xml',
        'views/res_company_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_employee_arl_risk.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_line_view.xml',
        'views/hr_contribution_register_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_payslip_edi_view.xml',
        'views/hr_payroll_structure_view.xml',
        'views/resource_calendar_view.xml',
        'views/account_view.xml',
        # Data
        'data/hr_contribution_register_data.xml',
        # 'data/hr_salary_rule_category_data.xml',
        # 'data/hr_salary_rule_data.xml',
        'data/hr_employee_arl_risk_data.xml',
        # 'data/hr_payroll_structure_data.xml',
        # Report
        'report/report_payslip.xml'
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    
}
