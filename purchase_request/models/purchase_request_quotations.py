from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import json
from dateutil.relativedelta import relativedelta

_STATES = [
    ("draft", "Draft"),
    ("sent", "Sent to Vendor"),
    ("quotation", "Quotation"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

_READONLY_STATES = [
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestQuotation(models.Model):
    _name = "purchase.request.quotation"
    _description = "Purchase Request Line Quotations"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request.quotation")

    name = fields.Char(string="Quotation Reference", required=True, default=lambda self: _("New"))
    partner_ref = fields.Char('Vendor Reference', copy=False,
                              help="Reference of the sales order or bid sent by the vendor. "
                                   "It's used to do the matching when you receive the "
                                   "products as this reference is usually written on the "
                                   "delivery order sent by your vendor.")
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True,  # states=_READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    date = fields.Date(string="Quotation date", default=fields.Date.context_today, tracking=True)
    date_expiration = fields.Date(string="Expiration date", required=True, tracking=True)
    description = fields.Text()
    company_id = fields.Many2one(comodel_name="res.company", default=lambda self: self.env.company)
    purchase_request_line_id = fields.Many2one(comodel_name="purchase.request.line", string="Request Line")
    quotation_line = fields.One2many(comodel_name="purchase.request.quotation.line", inverse_name="quotation_id",
                                     string="Quotation Products", readonly=False, copy=True, tracking=True)
    state = fields.Selection(selection=_STATES, string="Status", index=True, tracking=True, required=True, copy=False,
                             default="draft")
    # is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    currency_id = fields.Many2one(related="purchase_request_line_id.currency_id", string="Currency")
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    tax_totals_json = fields.Char(compute='_compute_tax_totals_json')
    date_calendar_start = fields.Datetime(compute='_compute_date_calendar_start', readonly=True, store=True)
    date_approve = fields.Datetime('Confirmation Date', readonly=1, index=True, copy=False)
    product_id = fields.Many2one('product.product', related='quotation_line.product_id', string='Product')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position',
                                         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    tax_country_id = fields.Many2one(
        comodel_name='res.country',
        compute='_compute_tax_country_id',
        # Avoid access error on fiscal position, when reading a purchase order with company != user.company_ids
        compute_sudo=True,
        help="Technical field to filter the available taxes depending on the fiscal country and fiscal position.")
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    notes = fields.Html('Terms and Conditions')
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',
                                              check_company=True, required=True,
                                              readonly=True,
                                              states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    best_quotation = fields.Boolean('Recommended by Purchase Dept.', default=False)
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase Order")
    modified_policy_order_id = fields.Many2one("purchase.order", string="Modified Policy Order")
    approval_user_id = fields.Many2one('res.users', string='Approval User', index=True, check_company=True)

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseRequestQuotation, self).default_get(fields_list)
        request_l = self.env['purchase.request.line'].browse(self._context.get('default_purchase_request_line_id'))
        if request_l:
            line = (0, 0, {'product_id': request_l.product_id.id, 'name': request_l.name,
                           'product_qty': request_l.product_qty, 'product_uom': request_l.product_uom_id.id,
                           'account_analytic_id': request_l.analytic_account_id.id,
                           'analytic_tag_ids': request_l.analytic_tag_ids})
            res.update({'quotation_line': [line], 'modified_policy_order_id': request_l.purchase_policy_order_id.id})
        return res

    @api.constrains('best_quotation')
    def _unique_best_quotation(self):
        for record in self:
            request_line = record.purchase_request_line_id
            if len(request_line.quotation_ids.filtered(lambda q: q.best_quotation)) > 1:
                raise ValidationError(_("Only 1 quotation can be set as the best for this purchase request line"))

    # @api.constrains('amount_total')
    # def _invalid_zero_total_quotation(self):
    #     for record in self:
    #         if record.amount_total == 0:
    #             raise ValidationError(_("Cannot Create a Zero value Quotation"))

    @api.depends('quotation_line.taxes_id', 'quotation_line.price_subtotal', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(quotation_line):
            return quotation_line.taxes_id._origin.compute_all(**quotation_line._prepare_compute_all_values())

        account_move = self.env['account.move']
        for quotation in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(quotation.quotation_line,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(quotation.partner_id, tax_lines_data, quotation.amount_total,
                                                      quotation.amount_untaxed, quotation.currency_id)
            quotation.tax_totals_json = json.dumps(tax_totals)

    @api.depends('company_id.account_fiscal_country_id', 'fiscal_position_id.country_id',
                 'fiscal_position_id.foreign_vat')
    def _compute_tax_country_id(self):
        for record in self:
            if record.fiscal_position_id.foreign_vat:
                record.tax_country_id = record.fiscal_position_id.country_id
            else:
                record.tax_country_id = record.company_id.account_fiscal_country_id

    @api.depends('state', 'date', 'date_approve')
    def _compute_date_calendar_start(self):
        for quotation in self:
            quotation.date_calendar_start = quotation.date_approve if (
                    quotation.state == 'done') else quotation.date

    @api.depends('quotation_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.quotation_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    def confirm_quotation(self):
        for record in self:
            if record.amount_total == 0 and not any(
                    record.quotation_line.mapped('product_id').mapped('is_policy_product')):
                raise ValidationError(_("Cannot Create a Zero value Quotation"))
            if record.name == _("New"):
                record.name = self._get_default_name()
            record.state = 'quotation'

    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        # self.state = 'sent'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('purchase_request.email_template_purchase_quotation')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.request.quotation',
            'active_model': 'purchase.request.quotation',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_lang([ctx['default_res_id']])[ctx['default_res_id']]

        self = self.with_context(lang=lang)
        ctx['model_description'] = _('Request for Quotation')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'draft').write({'state': 'sent'})
        return super(PurchaseRequestQuotation, self.with_context(
            mail_post_autofollow=self.env.context.get('mail_post_autofollow', True))).message_post(**kwargs)

    def request_approve(self):
        for record in self:
            request_line = record.purchase_request_line_id
            quotations_count = len(request_line.quotation_ids.filtered(lambda q: q.state == 'quotation'))
            if quotations_count < 3 and not request_line.product_id.allow_less_purchase_quotations:
                raise ValidationError(_("To request approbation there should be 3 quotations created"))

            if not record.approval_user_id:
                raise ValidationError(_("Please select the user that will approve this quotation."))
            assigned_to = record.approval_user_id

            request_line.state = 'to_approve'
            for quotation in request_line.quotation_ids.filtered(lambda q: q.state == 'quotation'):
                quotation.write({'state': 'to_approve', 'approval_user_id': assigned_to.id})
                update_log = self.env['purchase.request.log'].search(
                    [('request_line_id', '=', quotation.purchase_request_line_id.id)])
                update_log.write(
                    {'request_quotations_date': fields.Datetime.now(), 'request_quotations_user': self.env.user.id})
                quotation.purchase_request_line_id.assigned_to = assigned_to

            # Create Activity on Parent Purchase Request

            shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
            self.env['mail.activity'].create({
                'summary': 'Purchase Quotations Approval',
                'date_deadline': fields.Date.today() + relativedelta(days=shift),
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_model_id': self.env.ref("purchase_request.model_purchase_request").id,
                'res_id': record.purchase_request_line_id.request_id.id,
                'user_id': assigned_to.id,
                'note': _(
                    "Please %s review the information of the request line %s in which a quotation approval has been created") % (
                            assigned_to.name, record.purchase_request_line_id.name),
            })

    def button_approved(self):
        for record in self:
            request_line = record.purchase_request_line_id
            record.state = 'approved'
            record.date_approve = fields.Datetime.now()
            request_line.state = 'done'
            for quotation in request_line.quotation_ids.filtered(lambda q: q.id != record.id):
                quotation.state = 'rejected'

            pur_lines_dict = []
            for line in record.quotation_line:
                pur_lines_dict.append((0, 0, line.prepare_rfq_line_from_quotation()))

            new_po = self.env['purchase.order'].create({
                "partner_id": record.partner_id.id,
                "date_order": fields.Datetime.now(),
                'currency_id': record.currency_id.id,
                'origin': record.name,
                'order_line': pur_lines_dict,
                'modified_policy_order_id': record.modified_policy_order_id.id,
                'payment_term_id': record.invoice_payment_term_id.id,
                'project_id': self.env['project.project'].search(
                    [('analytic_account_id', '=', request_line.analytic_account_id.id)]).id,
            })

            record.purchase_order_id = new_po.id
            request_line.request_id.check_auto_done()

            update_log = self.env['purchase.request.log'].search(
                [('request_line_id', '=', record.purchase_request_line_id.id)])
            update_log.write({'purchase_order_id': new_po.id})

    def button_rejected(self):
        for record in self:
            request_line = record.purchase_request_line_id
            record.state = 'rejected'
            for quotation in request_line.quotation_ids.filtered(lambda q: q.id != record.id):
                quotation.state = 'rejected'

            # Create Activity on Parent Purchase Request
            assigned_to = self.company_id.purchase_quotations_approver
            shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
            self.env['mail.activity'].create({
                'summary': 'Purchase Quotations Rejection',
                'date_deadline': fields.Date.today() + relativedelta(days=shift),
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_model_id': self.env.ref("purchase_request.model_purchase_request").id,
                'res_id': record.purchase_request_line_id.request_id.id,
                'user_id': assigned_to.id,
                'note': _(
                    "Please %s review the information of the request line %s where the purchase quotations have been rejected") % (
                            assigned_to.name, record.purchase_request_line_id.name),
            })

            request_line.write({'state': 'rejected', 'assigned_to': assigned_to.id})

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequestQuotation, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        request_line = self.env['purchase.request.line'].browse(vals.get('purchase_request_line_id'))
        if request_line.state not in ("draft", "to_approve", "rejected"):
            raise ValidationError(_("Cannot create a new quotation for a line request the has been approved"))
        request = super(PurchaseRequestQuotation, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def unlink(self):
        for quotation in self:
            if quotation.state != "draft":
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequestQuotation, self).unlink()


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.quotation.line"
    _description = "Purchase Request Line"
    _order = "id desc"

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    date_planned = fields.Datetime(string='Delivery Date', index=True,
                                   help="Delivery date expected from vendor. This date respectively defaults to vendor pricelist lead time then today's date.")
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    product_type = fields.Selection(related='product_id.detailed_type', readonly=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    currency_id = fields.Many2one(related="quotation_id.currency_id", string="Currency")
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    quotation_id = fields.Many2one('purchase.request.quotation', string='Quotation Reference', index=True,
                                   required=True, ondelete='cascade')
    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Analytic Account',
                                          compute='_compute_account_analytic_id', readonly=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Analytic Tags',
                                        compute='_compute_analytic_tag_ids', readonly=False)
    company_id = fields.Many2one('res.company', related='quotation_id.company_id', string='Company', store=True,
                                 readonly=True)
    state = fields.Selection(related='quotation_id.state', store=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('product_id')
    def _compute_account_analytic_id(self):
        for rec in self:
            if not rec.display_type:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.quotation_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.quotation_id.date,
                    company_id=rec.quotation_id.company_id.id,
                )
                rec.account_analytic_id = default_analytic_account.analytic_id

    @api.depends('product_id')
    def _compute_analytic_tag_ids(self):
        for rec in self:
            if not rec.display_type:
                default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                    product_id=rec.product_id.id,
                    partner_id=rec.quotation_id.partner_id.id,
                    user_id=rec.env.uid,
                    date=rec.quotation_id.date,
                    company_id=rec.quotation_id.company_id.id,
                )
                rec.analytic_tag_ids = default_analytic_account.analytic_tag_ids

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency': self.quotation_id.currency_id,
            'quantity': self.product_qty,
            'product': self.product_id,
            'partner': self.quotation_id.partner_id,
        }

    def prepare_rfq_line_from_quotation(self):
        self.ensure_one()
        line_dict = {
            'product_id': self.product_id.id,
            'name': self.name,
            'product_uom': self.product_uom.id,
            'product_qty': self.product_qty,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'price_unit': self.price_unit,
            'partner_id': self.quotation_id.partner_id.id,
            'budget_line_segregation_id': self.quotation_id.purchase_request_line_id.budget_line_segregation_id.id,
            "purchase_request_lines": [(4, self.quotation_id.purchase_request_line_id.id)],
        }
        return line_dict
