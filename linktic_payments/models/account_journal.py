from odoo import fields, _, models, api
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    transitional_exception = fields.Boolean(string="Transitional Exception", default=False)
    related_company = fields.Many2one('res.company', string='Related Company', domain="[('id', '!=', company_id)]")
    loan_entry_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Loan Entry Account', domain="[('company_id', '=', company_id)]")
    loan_exit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Loan Exit Account', domain="[('company_id', '=', company_id)]")

    @api.constrains('related_company')
    def unique_inter_company_journal(self):
        for record in self:
            if record.related_company:
                if self.env['account.journal'].search_count([('related_company', '=', record.related_company.id)]) > 1:
                    old_journal_associated = self.env['account.journal'].search(
                        [('related_company', '=', record.related_company.id), ('id', '!=', record.id)])
                    raise ValidationError(
                        _(f"Company '{record.related_company.name}' is already associated to journal '{old_journal_associated.name}'."))

    @api.onchange('related_company')
    def reset_loan_accounts(self):
        for record in self:
            if not record.related_company:
                record.loan_entry_account_id = False
                record.loan_exit_account_id = False
