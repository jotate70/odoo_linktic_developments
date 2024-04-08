# Autor: Diego Torres
# Desarrollador y Consultor Odoo
# Linkedln: https://www.linkedin.com/in/diego-felipe-torres-reyes-083091152/
# Email: 20diegotorres01@gmail.com
# Github: DiTo1005
# Cel. +57 3108804090

{
    'name': 'Pagos Nómina - LinkTic SAS',
    'icon': '/lt_hr_payment/static/description/icon.png',
    'version': '1.0',
    'summary': 'Pagos de nómina LinkTic SAS',
    'description': """
        Este módulo realiza los pagos en el proceso de la nómina la empresa LinkTic SAS.
    """,
    'author': 'Diego Felipe Torres Reyes',
    'license': 'AGPL-3',
    'website': 'https://www.linktic.com',
    'category': 'Human Resources',
    'depends': ['om_hr_payroll_account'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/hr_payslip_view.xml',
        'views/hr_payslip_run_view.xml',
        # Wizard
        'wizard/payroll_payment_views.xml'
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    
}
