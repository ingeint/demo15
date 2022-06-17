from odoo import fields, models, api


class IngTax(models.Model):
    _inherit = 'account.tax'

    config_w_ids = fields.One2many('withholding.calc', 'tax_id')
    config_w_base_ids = fields.One2many('withholding.calc', 'tax_base_id')
    withholding_move_id = fields.One2many('account.move.withholding', 'tax_withholding_id')
    is_withholding = fields.Boolean(default=False)


class IngTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    is_withholding = fields.Boolean(default=False)
