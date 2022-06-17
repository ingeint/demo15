from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'res.company'

    tax_payer_type_id = fields.Many2one('tax.payer.type')
