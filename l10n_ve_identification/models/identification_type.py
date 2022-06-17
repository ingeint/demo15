from odoo import fields, models, api


class IdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'

    code = fields.Char(required=True)
