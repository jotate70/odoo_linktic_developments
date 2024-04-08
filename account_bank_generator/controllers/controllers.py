# -*- coding: utf-8 -*-
# from odoo import http


# class AccountBankPaymentTxtGenerator(http.Controller):
#     @http.route('/account_bank_generator/account_bank_generator/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_bank_generator/account_bank_generator/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_bank_generator.listing', {
#             'root': '/account_bank_generator/account_bank_generator',
#             'objects': http.request.env['account_bank_generator.account_bank_generator'].search([]),
#         })

#     @http.route('/account_bank_generator/account_bank_generator/objects/<model("account_bank_generator.account_bank_generator"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_bank_generator.object', {
#             'object': obj
#         })
