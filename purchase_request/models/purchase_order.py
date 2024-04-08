from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    contract_attachment = fields.Binary(string="Contract Attachment")
    contract_att_name = fields.Char(string="Contract Attachment Name")
    policy_attachment = fields.Binary(string="Policy Attachment")
    policy_att_name = fields.Char(string="Policy Attachment Name")
    need_contract = fields.Boolean(string="Needs Contract Attached", compute="_get_po_needs_contract", store=True,
                                   default=False)
    need_policy = fields.Boolean(string="Needs Policy Attached", compute="_get_po_needs_contract", store=True,
                                 default=False)
    mandatory_policy = fields.Boolean(string='Mandatory Policy', compute="_get_po_needs_contract", store=True,
                                      default=False)
    project_id = fields.Many2one('project.project', 'Project')
    modified_policy_order_id = fields.Many2one("purchase.order", string="Modified Policy Order")
    approved_policy_payment = fields.Boolean(string='Approved Policy Manager', copy=False)
    need_policy_payment_approval = fields.Boolean(string='Need Policy Payment Approval',
                                                  compute='set_need_policy_payment_approval')
    state = fields.Selection(selection_add=[('policy_approval', 'Policy Approval')])
    can_approve_policy_po = fields.Boolean(string="Can Approve Policy PO", compute="get_policy_po_approvers")

    def get_policy_po_approvers(self):
        for record in self:
            record.can_approve_policy_po = self.env.user in (
            self.company_id.policy_quotations_approver, self.env.ref('base.user_admin'))

    def set_need_policy_payment_approval(self):
        for record in self:
            policy_products = record.order_line.filtered(lambda
                                                             l: l.product_id.is_policy_product and l.account_analytic_id == l.order_id.company_id.analytic_account_policy)
            if policy_products:
                record.need_policy_payment_approval = True
            else:
                record.need_policy_payment_approval = False

    def button_accept_policy(self):
        self.write({'approved_policy_payment': True, 'state': 'purchase'})

        for picking in self.picking_ids.filtered(lambda p: p.state == 'assigned'):
            for line in picking.move_ids_without_package:
                line.quantity_done = line.product_uom_qty

            picking.button_validate()

        # Create Activity
        shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
        self.env['mail.activity'].create({
            'summary': 'Accepted Policy Purchase Order',
            'date_deadline': fields.Date.today() + relativedelta(days=shift),
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'res_model_id': self.env.ref("purchase.model_purchase_order").id,
            'res_id': self.id,
            'user_id': self.company_id.purchase_quotations_manager.id,
            'note': _(
                "Please %s review the information of the purchase order %s which have been approved and can be invoiced.") % (
                        self.company_id.purchase_quotations_manager.name, self.name),
        })

    @api.depends('order_line.price_subtotal')
    def _get_po_needs_contract(self):
        for record in self:
            policy_products = self.order_line.mapped('product_id').mapped('is_policy_product')
            if True in policy_products:
                record.need_policy = True
                record.need_contract = False
                record.mandatory_policy = False
            else:
                record.need_contract = record.amount_total > record.company_id.need_contract_purchase_amount and record.company_id.need_contract_purchase_amount > 0
                record.need_policy = record.amount_total > record.company_id.need_policy_purchase_amount and record.company_id.need_policy_purchase_amount > 0
                record.mandatory_policy = True

    def _purchase_request_confirm_message_content(self, request, request_dict=None):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _("Order confirmation %(po_name)s for your Request %(pr_name)s") % {
            "po_name": self.name,
            "pr_name": request.name,
        }
        message = "<h3>%s</h3><ul>" % title
        message += _(
            "The following requested items from Purchase Request %(pr_name)s "
            "have now been confirmed in Purchase Order %(po_name)s:"
        ) % {
                       "po_name": self.name,
                       "pr_name": request.name,
                   }

        for line in request_dict.values():
            message += _(
                "<li><b>%(prl_name)s</b>: Ordered quantity %(prl_qty)s %(prl_uom)s, "
                "Planned date %(prl_date_planned)s</li>"
            ) % {
                           "prl_name": line["name"],
                           "prl_qty": line["product_qty"],
                           "prl_uom": line["product_uom"],
                           "prl_date_planned": line["date_planned"],
                       }
        message += "</ul>"
        return message

    def _purchase_request_confirm_message(self):
        request_obj = self.env["purchase.request"]
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        "name": request_line.name,
                        "product_qty": line.product_qty,
                        "product_uom": line.product_uom.name,
                        "date_planned": date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id]
                )
                request.message_post(
                    body=message, subtype_id=self.env.ref("mail.mt_comment").id
                )
        return True

    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == "done":
                        raise exceptions.UserError(
                            _("Purchase Request %s has already been completed")
                            % (request_line.request_id.name)
                        )
        return True

    def button_confirm(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).button_confirm()
        self._purchase_request_confirm_message()
        return res

    def button_cancel(self):
        if self.need_policy_payment_approval and self.state == 'policy_approval':
            # Create Activity
            shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
            self.env['mail.activity'].create({
                'summary': 'Rejected Policy Purchase Order',
                'date_deadline': fields.Date.today() + relativedelta(days=shift),
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_model_id': self.env.ref("purchase.model_purchase_order").id,
                'res_id': self.id,
                'user_id': self.company_id.purchase_quotations_manager.id,
                'note': _(
                    "Please %s review the information of the purchase order %s which have been rejected.") % (
                            self.company_id.purchase_quotations_manager.name, self.name),
            })
        return super(PurchaseOrder, self).button_cancel()

    def unlink(self):
        alloc_to_unlink = self.env["purchase.request.allocation"]
        for rec in self:
            for alloc in (
                    rec.order_line.mapped("purchase_request_lines")
                            .mapped("purchase_request_allocation_ids")
                            .filtered(lambda alloc: alloc.purchase_line_id.order_id.id == rec.id)
            ):
                alloc_to_unlink += alloc
        res = super().unlink()
        alloc_to_unlink.unlink()
        return res

    def button_confirm(self):
        policy_products = self.order_line.mapped('product_id').mapped('is_policy_product')
        if True not in policy_products:
            if self.amount_total > self.company_id.need_contract_purchase_amount and self.company_id.need_contract_purchase_amount > 0 and not self.contract_attachment:
                amount_str = '{:,.0f}'.format(self.company_id.need_contract_purchase_amount).replace(',', '.')
                raise ValidationError(
                    _(f'Purchases above {amount_str} must have attachment of a contract and policy on contract attachment field'))
            if self.amount_total > self.company_id.need_policy_purchase_amount and self.company_id.need_policy_purchase_amount > 0 and not self.policy_attachment:
                amount_str = '{:,.0f}'.format(self.company_id.need_contract_purchase_amount).replace(',', '.')
                raise ValidationError(
                    _(f'Purchases above {amount_str} must have attachment of a contract and policy on contract attachment field'))
        return super(PurchaseOrder, self).button_confirm()

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['approved_manager'] = self.payment_term_id == self.env.ref('purchase_request.credit_card_payment_term')
        return res

    def action_create_invoice(self):
        policy_not_approved = self.filtered(lambda p: p.need_policy_payment_approval and not p.approved_policy_payment)
        if policy_not_approved:
            raise ValidationError(_("The following policy purchase orders are not approved by policy manager:\n\n"
                                    "%s") % ','.join(policy_not_approved.mapped('name')))

        res = super(PurchaseOrder, self).action_create_invoice()
        if res.get('res_id'):
            invoices = self.env['account.move'].browse(res.get('res_id'))
        elif res.get('domain'):
            invoices = self.env['account.move'].browse(res.get('domain')[0][2])
        for invoice in invoices:
            if invoice.invoice_payment_term_id == self.env.ref('purchase_request.credit_card_payment_term'):
                invoice.invoice_date = fields.Date.today()
                invoice.scheduled_payment_day = fields.Date.today()
                invoice.payment_journal_id = self.company_id.purchase_credit_card.id
                invoice.action_post()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_lines = fields.Many2many(
        comodel_name="purchase.request.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_order_line_id",
        column2="purchase_request_line_id",
        readonly=True,
        copy=False,
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_line_id",
        string="Purchase Request Allocation",
        copy=False,
    )
    budget_line_segregation_id = fields.Many2one('crossovered.budget.lines.segregation',
                                                 string='Budget Line Segregation',
                                                 copy=False)
    order_modified_policy_order_id = fields.Many2one("purchase.order", related="order_id.modified_policy_order_id")
    order_state = fields.Selection(
        [('draft', 'RFQ'), ('sent', 'RFQ Sent'), ('to approve', 'To Approve'), ('purchase', 'Purchase Order'),
         ('done', 'Locked'), ('cancel', 'Cancelled')
         ], related="order_id.state")
    order_invoice_status = fields.Selection(
        [('no', 'Nothing to Bill'), ('to invoice', 'Waiting Bills'), ('invoiced', 'Fully Billed')],
        related="order_id.invoice_status")

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({'budget_line_segregation_id': self.budget_line_segregation_id.id})
        return res

    def action_open_request_line_tree_view(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [("id", "in", request_line_ids)]

        return {
            "name": _("Purchase Request Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request.line",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        all_list = []
        for v in val:
            all_ids = self.env["purchase.request.allocation"].search(
                [("purchase_line_id", "=", v["purchase_line_id"])]
            )
            for all_id in all_ids:
                all_list.append((4, all_id.id))
            v["purchase_request_allocation_ids"] = all_list
        return val

    def update_service_allocations(self, prev_qty_received):
        for rec in self:
            allocation = self.env["purchase.request.allocation"].search(
                [
                    ("purchase_line_id", "=", rec.id),
                    ("purchase_line_id.product_id.type", "=", "service"),
                ]
            )
            if not allocation:
                return
            qty_left = rec.qty_received - prev_qty_received
            for alloc in allocation:
                allocated_product_qty = alloc.allocated_product_qty
                if not qty_left:
                    alloc.purchase_request_line_id._compute_qty()
                    break
                if alloc.open_product_qty <= qty_left:
                    allocated_product_qty += alloc.open_product_qty
                    qty_left -= alloc.open_product_qty
                    alloc._notify_allocation(alloc.open_product_qty)
                else:
                    allocated_product_qty += qty_left
                    alloc._notify_allocation(qty_left)
                    qty_left = 0
                alloc.write({"allocated_product_qty": allocated_product_qty})

                message_data = self._prepare_request_message_data(
                    alloc, alloc.purchase_request_line_id, allocated_product_qty
                )
                message = self._purchase_request_confirm_done_message_content(
                    message_data
                )
                alloc.purchase_request_line_id.request_id.message_post(
                    body=message, subtype_id=self.env.ref("mail.mt_comment").id
                )

                alloc.purchase_request_line_id._compute_qty()
        return True

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _("Service confirmation for Request %s") % (
            message_data["request_name"]
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested services from Purchase"
            " Request %(request_name)s requested by %(requestor)s "
            "have now been received:"
        ) % {
                       "request_name": message_data["request_name"],
                       "requestor": message_data["requestor"],
                   }
        message += "<ul>"
        message += _(
            "<li><b>%(product_name)s</b>: "
            "Received quantity %(product_qty)s %(product_uom)s</li>"
        ) % {
                       "product_name": message_data["product_name"],
                       "product_qty": message_data["product_qty"],
                       "product_uom": message_data["product_uom"],
                   }
        message += "</ul>"
        return message

    def _prepare_request_message_data(self, alloc, request_line, allocated_qty):
        return {
            "request_name": request_line.request_id.name,
            "product_name": request_line.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": alloc.product_uom_id.name,
            "requestor": request_line.request_id.requested_by.partner_id.name,
        }

    def write(self, vals):
        #  As services do not generate stock move this tweak is required
        #  to allocate them.
        prev_qty_received = {}
        if vals.get("qty_received", False):
            service_lines = self.filtered(lambda l: l.product_id.type == "service")
            for line in service_lines:
                prev_qty_received[line.id] = line.qty_received
        res = super(PurchaseOrderLine, self).write(vals)
        if prev_qty_received:
            for line in service_lines:
                line.update_service_allocations(prev_qty_received[line.id])
        return res
