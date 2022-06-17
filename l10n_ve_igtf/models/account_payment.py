from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Description'

    payment_reference_id = fields.Many2one('account.payment', copy=False)
    amount_igtf = fields.Float(copy=False)
    percent_igtf = fields.Float(copy=False)
    generate_igtf = fields.Boolean(copy=False, default=False)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Description'

    amount_igtf = fields.Float(copy=False)
    percent_igtf = fields.Float(copy=False)
    generate_igtf = fields.Boolean(copy=False, default=False)

    @api.onchange('generate_igtf', 'amount')
    def calculate_igtf(self):
        if self.generate_igtf and self.amount > 0.0:
            ConfigIgtf = self.env['ingein.config.igtf'].search([('company_id', '=', self.company_id.id)])
            percent = ConfigIgtf.percent_igtf
            self.percent_igtf = percent
            self.amount_igtf = percent / 100 * self.amount

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'amount_igtf': self.amount_igtf,
            'percent_igtf': self.percent_igtf,
            'generate_igtf': self.generate_igtf
        }
        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals
        return super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()

    '''
    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        if self.amount_igtf > 0 and self.generate_igtf:
            payment_igtf_vals = {
                'date': self.payment_date,
                'amount': self.amount_igtf,
                'payment_type': self.payment_type,
                'partner_type': self.partner_type,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'partner_bank_id': self.partner_bank_id.id,
                'payment_method_id': self.payment_method_id.id,
                'destination_account_id': self.line_ids[0].account_id.id}
            payments_igtf = self.env['account.payment'].create(payment_igtf_vals)
        return res
    '''