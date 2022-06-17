from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    tax_payer_type_id = fields.Many2one('tax.payer.type')
