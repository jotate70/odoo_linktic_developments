from odoo import fields, _, models, api
from odoo.exceptions import ValidationError

class RequestForBonuses(models.Model):
    _name = "request.bonuses"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "request for bonuses"
    
    name = fields.Char(string="bonus",readonly=True,select=True,copy=False,default='New')
    bonuses_document = fields.Binary(string="Bonuses Committee")
    bonuses_document_name = fields.Char(string="Bonuses Committee")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('finance_leader_approval_pending', 'Finance leader approval pending'),
                                        ('human_talent_approval_pending', 'Human talent approval pending'),
                                        ('pending_approval_vice_presidency', 'Pending approval Vice Presidency'),
                                        ('under_review_accounting', 'Under review Accounting'),
                                        ('approved', 'Approved'),
                                        ('decline','Decline')],
                                        string='state',
                                        store=True,
                                        default='draft')
    notes = fields.Text(string='Note')
    charge_account_ids = fields.One2many(comodel_name='hr.contractor.charge.account', inverse_name='request_bonuses_id', string='Employee bonuses')
    bonus_line_ids = fields.One2many(comodel_name='hr.contractor.charge.account.line',inverse_name='request_bonuses_id',string='Bonus Line')
    Types_bonuses = fields.Selection(selection=[('leaders', 'Leaders'),
                                        ('commercial_personnel', 'Commercial Personnel'),
                                        ('project_managers', 'Project Managers'),
                                        ('individuals_or_worker', 'Individuals or worker'),],
                                        string='Types bonuses',
                                        store=True,
                                        default='individuals_or_worker')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, default=lambda self: self.env.company)
    activity_id = fields.Integer(string='Activity')
    journal_bonus_id = fields.Many2one('account.journal', string='Charge Account Journal',related='company_id.bonus_charge_default_journal_id')
    invoice_count = fields.Integer(string='Count invoices',compute="compute_invoices_count", default=0)
    invoice_ids2 = fields.One2many(comodel_name="account.move",inverse_name="bonuses_id",string="Bills")
    invoice_count_published = fields.Integer(string='Count invoices',compute="compute_invoices_count_published", default=0)
    financial_lead_approver_id = fields.Many2one('res.users', string="approver",related='company_id.financial_lead_approver_id')
    approver_th_id = fields.Many2one('res.users', string="approver",related='company_id.approver_th_id')
    vice_president_approver_id = fields.Many2one('res.users', string="approver",related='company_id.vice_president_approver_id')
    accounting_approver_id = fields.Many2one('res.users', string="approver",related='company_id.accounting_approver_id')
    
    def cancel_bonus(self):
        self.state='decline'
        if self.charge_account_ids:
            for account_id in self.charge_account_ids:
                for invoice_id in account_id.invoice_ids:
                    invoice_id.state = 'cancel'
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {'activity_type_id': 4,
                        'summary': 'Bonificación cancelada',
                        'automated': True,
                        'note': 'Cancelación de bonificación',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': model_id,
                        'res_id': self.id,
                        'user_id': self.create_uid.id,
                        }
        new_activity = self.env['mail.activity'].create(create_vals)
        self.write({'activity_id': new_activity})
        
    def go_to_financial(self):
        self.state='finance_leader_approval_pending'
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Aprobado')
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {'activity_type_id': 4,
                        'summary': 'Bonificación enviada a validar por financiera',
                        'automated': True,
                        'note': 'Bono enviado a financiera',
                        'date_deadline': fields.datetime.now(),
                        'res_model_id': model_id,
                        'res_id': self.id,
                        'user_id': self.create_uid.id,
                        }
        new_activity = self.env['mail.activity'].create(create_vals)
        self.write({'activity_id': new_activity})
        

    def request_hr_approval(self):
        if self.company_id.financial_lead_approver_id == self.env.user:
            self.state='human_talent_approval_pending'
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Aprobado por financiera',
                           'automated': True,
                           'note': 'Solicitud de aprobación por vicepresidencia',
                           'date_deadline': fields.datetime.now(),
                           'res_model_id': model_id,
                           'res_id': self.id,
                           'user_id': self.company_id.financial_lead_approver_id.id,
                           }
            new_activity = self.env['mail.activity'].create(create_vals)
            self.write({'activity_id': new_activity})
        else:
            raise ValidationError(_('This action can only be performed by the assigned approved person.'))
    
    def vice_presidency_approval(self):
        if self.company_id.approver_th_id == self.env.user:
            self.state='pending_approval_vice_presidency'
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es Aprobado')
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Aprobado por talento humano.',
                           'automated': True,
                           'note': 'Solicitud de aprobación, Vicepresidencia',
                           'date_deadline': fields.datetime.now(),
                           'res_model_id': model_id,
                           'res_id': self.id,
                           'user_id': self.company_id.approver_th_id.id,
                           }
            new_activity = self.env['mail.activity'].create(create_vals)
            self.write({'activity_id': new_activity})
        else:
            raise ValidationError(_('This action can only be performed by the assigned approved person.'))
    
    def request_accounting_review(self):
        if self.company_id.vice_president_approver_id == self.env.user:
            self.create_contractor_bill()
            self.state='under_review_accounting'
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es Aprobado')
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Aprobado por vicepresidencia',
                           'automated': True,
                           'note': 'Solicitud de aprobación Contabilidad',
                           'date_deadline': fields.datetime.now(),
                           'res_model_id': model_id,
                           'res_id': self.id,
                           'user_id': self.company_id.vice_president_approver_id.id,
                           }
            new_activity = self.env['mail.activity'].create(create_vals)
            self.write({'activity_id': new_activity})
        else:
            raise ValidationError(_('This action can only be performed by the assigned approved person.'))
        
    def request_approval(self):
        if self.company_id.accounting_approver_id == self.env.user:
            self.state='approved'
            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
            new_activity.action_feedback(feedback='Es Aprobado')
            model_id = self.env['ir.model']._get(self._name).id
            create_vals = {'activity_type_id': 4,
                           'summary': 'Bonificación aprobada por contabilidad',
                           'automated': True,
                           'note': 'Bono aprobado',
                           'date_deadline': fields.datetime.now(),
                           'res_model_id': model_id,
                           'res_id': self.id,
                           'user_id': self.company_id.accounting_approver_id.id,
                           }
            new_activity = self.env['mail.activity'].create(create_vals)
            self.write({'activity_id': new_activity})
    @api.model
    def create(self, vals):
        if vals.get('name','New') == 'New':
            vals['name']=self.env['ir.sequence'].next_by_code('bonus.ifpv') or 'New'
        return super(RequestForBonuses,self).create(vals)
    
    def create_contractor_bill(self):
        for record in self:
            for account in record.charge_account_ids:
                bonus_line_list = []
                for line in account.bonus_line_ids:
                    bonus_line_list.append((0, 0, line._bonus_prepare_account_move_line()))
                bill_header_values = {
                    'bonuses_id': record.id,
                    'hr_contractor_charge_account_id': account.id,
                    'partner_id': account.employee_id.sudo().address_home_id.id,
                    'invoice_date': fields.Date.today(),
                    'date': fields.Date.today(),
                    'move_type': 'in_invoice',
                    'journal_id': account.journal_bonus_id.id,
                    'invoice_line_ids': bonus_line_list,
                    'company_id': account.employee_company_id.id,
                }

                self.env['account.move'].create(bill_header_values)
    
    def get_invoices(self):
        invoices = self.charge_account_ids.invoice_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
    
    def get_invoices_published(self):
        invoices = self.charge_account_ids.invoice_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids),('state','=','posted')]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
        
    def compute_invoices_count(self):
        for record in self:
            record.invoice_count = len(record.charge_account_ids.invoice_ids)
    
    def compute_invoices_count_published(self):
        for record in self:
            con = 0
            for account in record.charge_account_ids.invoice_ids:
               if account.state == 'posted':
                   con=con+1 
            record.invoice_count_published = con