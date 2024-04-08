# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    def _get_default_assigned_to(self):
        return self.env["res.users"].browse(self.env.company.purchase_request_approver.id)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        tracking=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
        default=_get_default_assigned_to,
        index=True,
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    assigned_to_editable = fields.Boolean(compute="_compute_assigned_to_is_editable")
    can_approve_request = fields.Boolean(compute="_compute_can_approve_request")
    can_close_request = fields.Boolean(compute="_compute_can_close_request")
    can_edit_line_description = fields.Boolean(compute="_compute_can_edit_line_description", default="True")
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        required=True,
        default=_default_picking_type,
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Total Estimated Cost",
        store=True,
    )
    project_id = fields.Many2one('project.project', 'Project')
    is_closed = fields.Boolean(string="Is Closed", default=False)

    def _compute_assigned_to_is_editable(self):
        for rec in self:
            if rec.state == "to_approve" and self.env.user.has_group("purchase_request.group_purchase_request_manager"):
                rec.assigned_to_editable = True
            else:
                rec.assigned_to_editable = False

    def _compute_can_approve_request(self):
        for rec in self:
            if (self.env.user == rec.assigned_to or self.env.user == self.env.ref(
                    'base.user_admin')) and rec.state == "to_approve":
                rec.can_approve_request = True
            else:
                rec.can_approve_request = False

    def _compute_can_close_request(self):
        for rec in self:
            if self.env.user in (rec.company_id.purchase_quotations_manager,
                                 self.env.ref('base.user_admin')) and rec.state == "approved":
                rec.can_close_request = True
            else:
                rec.can_close_request = False

    def _compute_can_edit_line_description(self):
        for rec in self:
            if (self.env.user in (rec.company_id.purchase_quotations_manager,
                                 self.env.ref('base.user_admin')) and rec.state == "approved") or rec.state == "draft":
                rec.can_edit_line_description = True
            else:
                rec.can_edit_line_description = False

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_estimated_cost(self):
        for rec in self:
            rec.estimated_cost = sum(rec.line_ids.mapped("estimated_cost"))

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))

    def action_view_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        lines = self.mapped("line_ids.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # remove default filters
        action["context"] = {}
        lines = self.mapped(
            "line_ids.purchase_request_allocation_ids.stock_move_id.picking_id"
        )
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = (
            self.env.ref("purchase_request.purchase_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._get_default_name()
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_to_approve(self):
        self.to_approve_allowed_check()

        if any(not line.budget_line_segregation_id for line in self.line_ids):
            raise ValidationError(_("All lines must have a segregation selected"))

        # Create or update log for each line in the request
        for line in self.line_ids:
            update_log = self.env['purchase.request.log'].search(
                [('request_line_id', '=', line.id)])
            if update_log:
                if line.state != 'done':
                    update_log.write(
                        {'request_creation_date': fields.Datetime.now(),
                         'request_creation_user': self.env.user.id,
                         'request_approve_date': False,
                         'request_approve_user': False,
                         'request_quotations_date': False,
                         'request_quotations_user': False,
                         'request_quotations_user': False,
                         }
                    )
            else:
                self.env['purchase.request.log'].create(
                    {'request_line_id': line.id, 'request_creation_date': fields.Datetime.now(),
                     'request_creation_user': self.env.user.id})
            line.assigned_to = self.assigned_to

        # Create Activity
        shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
        self.env['mail.activity'].create({
            'summary': 'Purchase Request Approval',
            'date_deadline': fields.Date.today() + relativedelta(days=shift),
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'res_model_id': self.env.ref("purchase_request.model_purchase_request").id,
            'res_id': self.id,
            'user_id': self.assigned_to.id,
            'note': _(
                "Please %s review the information of the request %s in which a request approval has been created") % (
                    self.assigned_to.name, self.name),
        })

        return self.write({"state": "to_approve"})

    def button_approved(self):
        if not self.company_id.purchase_quotations_manager:
            raise ValidationError(
                _("There is no default Purchase Quotation Approver defined, please set on settings/purchase menu"))

        # Update logs for each line of the request
        for line in self.line_ids:
            update_log = self.env['purchase.request.log'].search([('request_line_id', '=', line.id)])
            update_log.write(
                {'request_approve_date': fields.Datetime.now(), 'request_approve_user': self.env.user.id})
            line.assigned_to = self.company_id.purchase_quotations_manager

        # Create Activity
        shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
        self.env['mail.activity'].create({
            'summary': 'Request Purchase Quotations',
            'date_deadline': fields.Date.today() + relativedelta(days=shift),
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'res_model_id': self.env.ref("purchase_request.model_purchase_request").id,
            'res_id': self.id,
            'user_id': self.company_id.purchase_quotations_manager.id,
            'note': _(
                "Please %s review the information of the request %s which have been approved and needs purchase quotations") % (
                    self.company_id.purchase_quotations_manager.name, self.name),
        })

        return self.write({"state": "approved"})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    def button_done(self):
        for line in self.line_ids.filtered(lambda l: l.state != 'done'):
            line.state = 'closed'
        return self.write({"state": "done", "is_closed": True})

    def button_restore_closed(self):
        for line in self.line_ids.filtered(lambda l: l.state == 'closed'):
            line.state = 'draft'
        return self.write({"state": "approved", "is_closed": False})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )

    def check_auto_done(self):
        """When all lines are done the purchase request should be change to done."""
        for pr in self:
            if set(pr.line_ids.mapped("state")) == {'done'}:
                pr.write({"state": "done"})

    @api.onchange("line_ids")
    def _check_product_lines_policy(self):
        """checks if there is a line with policy type product and forces that all the lines have this type of items
        and checks if all lanes are policy type that only 2 analytic_account are used at the same time"""
        if len(set(self.line_ids.mapped('product_id').mapped('is_policy_product'))) > 1:
            raise ValidationError(_("A purchase request with policy lines cannot have another type of items"))

        if all(self.line_ids.mapped('product_id').mapped('is_policy_product')):
            if len(set(self.line_ids.mapped('analytic_account_id'))) > 2:
                raise ValidationError(_("A purchase request with policy lines can only have 2 different analytic accounts"))
