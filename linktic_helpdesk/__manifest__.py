# Copyright 2023 Linktic - Omar Amaya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Linktic Helpdesk Customization",
    'summary': 'Customization to Helpdesk module',
    "version": "15.0.1.0.0",
    'category': 'Services/Helpdesk',
    "author": "Omar Amaya",
    "license": "AGPL-3",
    "depends": ["helpdesk_mgmt", "linktic_budget"],

    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_category_views.xml',
        'views/helpdesk_ticket_stage_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_menu.xml',
        'views/helpdesk_ticket_team_views.xml',
        'views/helpdesk_stage_category_relation_views.xml',
        'wizard/helpdesk_ticket_stage_transition_wizard_views.xml',
        'wizard/helpdesk_update_contract_changes_wizard_views.xml',
    ],
}
