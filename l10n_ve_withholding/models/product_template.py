from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    withholding_category_id = fields.Many2one('withholding.category')
    tax_group_id = fields.Many2one('account.tax.group', 'Group Tax')

    


