from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMoveWithholding(models.Model):
    _name = 'account.move.withholding'
    _description = 'Relationship between invoice and withholdings'

    move_id = fields.Many2one('account.move', 'Invoice')
    name = fields.Char()
    company_id = fields.Many2one('res.company')
    type_withholding_purchase_id = fields.Many2one('withholding.type', 'Type Withholding')
    type_withholding_sale_id = fields.Many2one('withholding.type', 'Type Withholding')
    tax_withholding_id = fields.Many2one('account.tax', 'Tax Withholding',
                                         domain="['|', ('config_w_ids.withholding_id.id', '=', "
                                                "type_withholding_purchase_id), ('config_w_ids.withholding_id.id', "
                                                "'=', type_withholding_sale_id)]")
    base_amount_tax = fields.Float()
    percent_tax = fields.Float()
    tax_total = fields.Float()
    is_processed = fields.Boolean(default=False)
    rules_id = fields.Many2one('withholding.rules', 'Withholding Rules')
    document_no = fields.Char()
    description = fields.Char()
    date_trx = fields.Date()
    date_post = fields.Date()
    type = fields.Char()
    wh_processed = fields.Boolean()
    move_type = fields.Selection(selection=[
        ('entry', 'Journal Entry'),
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('in_invoice', 'Vendor Bill'),
        ('in_refund', 'Vendor Credit Note'),
        ('out_receipt', 'Sales Receipt'),
        ('in_receipt', 'Purchase Receipt'),
    ], related='move_id.move_type')

    @api.constrains('move_id')
    def set_name(self):
        for line in self:
            line.name = line.tax_withholding_id.name

    @api.constrains('move_id')
    def set_gen_payment(self):
        moves = self.env['account.move'].search([('id', '=', self.move_id.id)])
        for rec in moves:
            rec.withholding_generate = True

    @api.onchange('tax_withholding_id', 'base_amount_tax')
    def set_tax_percent(self):
        subtracting = 0
        if self.rules_id:
            subtracting = self.rules_id.withholding_calc_id.subtracting

        self.percent_tax = self.tax_withholding_id.amount
        amount = ((self.base_amount_tax * self.percent_tax) / 100)
        cal_total_tax = amount - subtracting
        if cal_total_tax < 0:
            self.tax_total = 0
        else:
            self.tax_total = cal_total_tax

    @api.onchange('type_withholding_purchase_id', 'type_withholding_sale_id')
    def clean_val_by_types(self):
        self.write({'percent_tax': 0,
                    'tax_total': 0,
                    'base_amount_tax': 0,
                    'tax_withholding_id': False})

    @api.onchange('base_amount_tax')
    def validate_amount(self):
        if self.base_amount_tax > 0 and self.base_amount_tax > self.move_id.amount_untaxed:
            self.base_amount_tax = 0
            self.tax_total = 0
            message = _((
                            'The base placed cannot be greater than the base of the invoice, the base is: %s ') % (
                            str(self.move_id.amount_untaxed)))
            mess = {'title': _('Wrong invoice base!'),
                    'message': message
                    }
            return {'warning': mess}

    @api.model
    def create_withholding(self,
                           company_id,
                           move_id,
                           type_withholding_purchase_id,
                           type_withholding_sale_id,
                           tax_withholding_id,
                           base_amount_tax,
                           rules_id,
                           document_no,
                           date_trx,
                           date_post,
                           type_invoice):

        vals = {
            'company_id': company_id,
            'move_id': move_id,
            'type_withholding_purchase_id': type_withholding_purchase_id,
            'type_withholding_sale_id': type_withholding_sale_id,
            'tax_withholding_id': tax_withholding_id,
            'base_amount_tax': base_amount_tax,
            'rules_id': rules_id,
            'document_no': document_no,
            'date_trx': date_trx,
            'date_post': date_post,
            'type': type_invoice,
        }
        withholding = self.sudo().create(vals)
        return withholding

    def unlink(self):
        for record in self:
            invoices = record.env['account.move'].search([('id', '=', record.move_id.id)])
            invoices.withholding_generate = False
        for wh_record in self:
            if wh_record.wh_processed:
                raise ValidationError('No puede borrar un retencion procesada')
        return super(AccountMoveWithholding, self).unlink()

    @api.model
    def create(self, vals_list):
        if 'move_id' in vals_list:
            move = self.env['account.move'].sudo().search([('id', '=', vals_list['move_id'])])
            if move.withholding_processed:
                raise ValidationError('You cannot create records if the invoice has withholdings processed')
        res = super(AccountMoveWithholding, self).create(vals_list)
        return res
