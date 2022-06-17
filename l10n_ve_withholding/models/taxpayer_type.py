from odoo import fields, models, api


class TaxPayerType(models.Model):
    _inherit = "tax.payer.type"

    rule_company_ids = fields.One2many('withholding.rules', 'tax_payer_company')
    rule_partner_ids = fields.One2many('withholding.rules', 'tax_payer_partner')

    


