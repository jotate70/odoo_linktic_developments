from odoo import fields, models, api, _


class LinkticReportCollectionAccounts(models.Model):
    _name = 'collection.accounts'
    _description = 'Report Collection Accounts'

    rut = fields.Char(string='RUT', size=100)
    bank_name = fields.Char(string='Bank Name', size=100)
    account_type = fields.Char(string='Account Type', size=100)
    number_account = fields.Char(string='Number Account', size=100)
    account_holder = fields.Char(string='Account Holder', size=100)
    document_type = fields.Char(string='Document Type', size=100)
    number_document = fields.Char(string='Number Document', size=100)
    payment_concept = fields.Char(string='Payment Concept', size=100)
    amount = fields.Char(string='Amount', size=100)
    personal_id = fields.Many2one(comodel_name='res.users', string='Personal', size=100)
    more_than_two_contractors = fields.Integer(string='More than two contractors', size=100)
    from_date = fields.Date(string='From Date', size=100)
    until_date = fields.Date(string='until Date', size=100)
    binance_email = fields.Char(string='Binance Email', size=100)
    binance_id = fields.Integer(string='Binance', size=11)
    binance_user = fields.Char(string='Binance User', size=100)
    binance_tron_usdt = fields.Char(string='Binance tron usdt', size=100)
    out_colombia = fields.Integer(string='Out Colombia', size=100)
    bank_outside_colombia = fields.Char(string='Bank Outside Colombia', size=100)
    signature = fields.Char(string='signature', size=100)
    file_url = fields.Char(string='file_url', size=100)
    document_other = fields.Char(string='document_other', size=100)
    binance_option = fields.Integer(string='Bank Outside Colombia', size=100)



