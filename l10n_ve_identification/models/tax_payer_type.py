from odoo import fields, models, api


class TaxPaperType(models.Model):
    _name = 'tax.payer.type'
    _description = 'Module for the user of the system ' \
                   'to register and update the types of ' \
                   'taxpayers to comply with Venezuelan legislation. ' \
                   'In Latin America there are different ' \
                   'types of taxpayers (Special Taxpayer, Ordinary 75% ... among others).'

    code = fields.Char(string='code')
    name = fields.Char(translate=True, required=True)
    description = fields.Char()
    active = fields.Boolean(default=True)

