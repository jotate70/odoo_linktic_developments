from odoo import api, fields, models, _
import base64


class SaleOrderAssignPolicy(models.TransientModel):
    _name = 'sale.order.assign.policy.wizard'
    _description = 'Assign Policy to Sale Order'

    sale_order_id = fields.Many2one('sale.order', required=True)
    policy_purchase_order_id = fields.Many2one('purchase.order', string="Policy Purchase Order",
                                               domain=[('mandatory_policy', '=', False), ('need_policy', '=', True),
                                                       ('project_id', '=', False)])

    def do_action(self):
        for record in self:
            record.sale_order_id.policy_purchase_order_id = record.policy_purchase_order_id

            record.policy_purchase_order_id.project_id = record.sale_order_id.project_ids[0]

            purchase_quotation = self.env['purchase.request.quotation'].search(
                [('purchase_order_id', '=', record.policy_purchase_order_id.id)])
            if purchase_quotation:
                purchase_quotation.purchase_request_line_id.request_id.project_id = record.sale_order_id.project_ids[0]
