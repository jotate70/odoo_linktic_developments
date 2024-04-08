# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import formatLang

STATUS_COLOR = {
    'suspended': 23,  # red / danger
    'canceled': 9,  # magenta
    'lapsed': 23,  # red / danger
    'on_sale': 4,  # light blue
    'sold': 20,  # green / success
    'support': 4,  # light blue
    False: 0,  # default grey -- for studio
}


class ProjectUpdate(models.Model):
    _inherit = 'project.update'

    status = fields.Selection(selection_add=[
        ('suspended', 'Suspended'),
        ('canceled', 'Canceled'),
        ('lapsed', 'Lapsed'),
        ('on_sale', 'On Sale'),
        ('sold', 'Sold Out'),
        ('support', 'Support'),
    ], ondelete={'suspended': 'set default', 'canceled': 'set default', 'lapsed': 'set default',
                 'on_sale': 'set default', 'sold': 'set default', 'support': 'set default'}
        , default='on_track')

    @api.depends('status')
    def _compute_color(self):
        for update in self:
            update.color = STATUS_COLOR.get(update.status)
            if not update.color:
                super(ProjectUpdate, update)._compute_color()
