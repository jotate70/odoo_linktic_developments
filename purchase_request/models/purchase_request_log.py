# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLog(models.Model):
    _name = "purchase.request.log"
    _description = "Purchase Request time Log"
    _order = "id desc"

    name = fields.Char(string="Request Log Reference", default=lambda self: "Log " + self.request_line_id.name)
    request_line_id = fields.Many2one("purchase.request.line", string="Request Line", ondelete='cascade')
    request_id = fields.Many2one("purchase.request", related="request_line_id.request_id", string="Purchase Request")
    product_id = fields.Many2one("product.product", related="request_line_id.product_id", string="Product", store="True")
    request_creation_date = fields.Datetime(string="Request Creation")
    request_creation_user = fields.Many2one("res.users", string="Request User")
    request_approve_date = fields.Datetime(string="Request Approbation")
    request_approve_user = fields.Many2one("res.users", string="Request Approbation User")
    request_quotations_date = fields.Datetime(string="Quotations Creation")
    request_quotations_user = fields.Many2one("res.users", string="Request Quotations User")
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_order_vendor = fields.Many2one("res.partner", string="Purchase Vendor",
                                            related="purchase_order_id.partner_id", store="True")
    purchase_creation_date = fields.Datetime(string="Purchase Order Creation", related="purchase_order_id.create_date")
    purchase_creation_user = fields.Many2one("res.users", string="Purchase Order User",
                                             related="purchase_order_id.create_uid")
    picking_id = fields.Many2one("stock.picking", string="Receipt")
    picking_validation_date = fields.Datetime(string="Receipt Validation")
    picking_validation_user = fields.Many2one("res.users", string="Receipt Validation User")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("purchase.request.quotation")
        return super(PurchaseRequestLog, self).create(vals)
