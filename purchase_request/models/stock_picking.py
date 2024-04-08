from odoo import models, fields, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for record in self:
            if record.purchase_id.need_policy and not record.purchase_id.policy_attachment:
                raise ValidationError(
                    _("The Purchase Order (%s) does not have a policy attached, please set a document in the PO and try again" % (
                        self.purchase_id.name)))

            # Update logs of each PO involved
            po_obj = record.purchase_id
            po_lines = record.purchase_id.order_line
            purchase_request_line = self.env['purchase.request.line'].search([('purchase_lines', 'in', po_lines.ids)])
            update_log = self.env['purchase.request.log'].search([('request_line_id', '=', purchase_request_line.id)])
            update_log.write({'picking_id': record.id, 'picking_validation_date': fields.Datetime.now(),
                              'picking_validation_user': self.env.user.id})

            # Check if is a policy PO and doesn't have approval to send it to the validation stage and don't do the
            # validation for the stock picking so the PO can be canceled
            if po_obj.need_policy_payment_approval and not po_obj.approved_policy_payment:
                if po_obj.state != 'policy_approval':
                    po_obj.state = 'policy_approval'

                    # Create Activity
                    shift = 1 + ((fields.Datetime.now().weekday() // 4) * (6 - fields.Datetime.now().weekday()))
                    self.env['mail.activity'].create({
                        'summary': 'Policy Purchase Order Approval',
                        'date_deadline': fields.Date.today() + relativedelta(days=shift),
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'res_model_id': self.env.ref("purchase.model_purchase_order").id,
                        'res_id': po_obj.id,
                        'user_id': self.company_id.policy_quotations_approver.id,
                        'note': _(
                            "Please %s review the information of the purchase order %s which needs to be approved") % (
                                    self.company_id.policy_quotations_approver.name, po_obj.name),
                    })

                    message_object = {
                        'value': {},
                        'warning': {
                            'title': _('Informative Message'),
                            'message': _('The PO is a policy related and needs to be approved'),
                        }
                    }

                    return message_object

                else:
                    raise ValidationError(
                        _("The PO related to this Picking has policy related items and must be approved by the correspondent user, when that PO is accepted this picking will be validated automatically"))

            if po_obj.need_policy_payment_approval and po_obj.approved_policy_payment:
                po_obj.state = 'purchase'

        res = super(StockPicking, self).button_validate()
        return res
