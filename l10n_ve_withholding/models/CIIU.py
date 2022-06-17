from odoo import fields, models, api


class CIUU(models.Model):
    _name = 'ciiu'
    _description = 'ciiu tax'

    partner_ids = fields.One2many('res.partner', 'ciiu_partner')
    company_ids = fields.One2many('res.company', 'ciiu_company')
    code = fields.Char()
    name = fields.Char()
    description = fields.Char()
    rule_company_ids = fields.One2many('withholding.rules', 'ciiu_company')
    rule_partner_ids = fields.One2many('withholding.rules', 'ciiu_partner')



