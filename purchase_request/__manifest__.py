# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "Purchase Request",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "15.0.1.1.0",
    "summary": "Use this module to have notification of requirements of "
    "materials and/or external services and keep track of such "
    "requirements.",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["purchase", "product", "purchase_stock", "linktic_budget"],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/account_payment_term_data.xml",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_quotation_sequence.xml",
        "data/purchase_request_data.xml",
        "reports/report_purchase_request.xml",
        "reports/request_quotation_reports.xml",
        "reports/purchase_request_quotation_templates.xml",
        "data/quotation_mail_template_data.xml",
        "wizard/purchase_request_line_make_purchase_order_view.xml",
        "views/purchase_request_view.xml",
        "views/purchase_request_line_view.xml",
        "views/purchase_request_report.xml",
        "views/product_template.xml",
        "views/purchase_order_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/purchase_request_quotations_views.xml",
        "views/res_config_settings_views.xml",
        "views/purchase_request_log_view.xml",
        'views/purchase_order_line_views.xml',
    ],
    "demo": ["demo/purchase_request_demo.xml"],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
