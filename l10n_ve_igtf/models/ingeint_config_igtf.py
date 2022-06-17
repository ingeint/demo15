from odoo import fields, models, api


class ConfigIgtf(models.Model):
    _name = 'ingein.config.igtf'
    _description = 'Configuration IGTF'

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', copy=False)
    percent_igtf = fields.Float()
