from odoo import fields, models, api


class WithholdingCategory(models.Model):
    _name = 'withholding.category'
    _description = 'Withholding category'

    code = fields.Char()
    name = fields.Char()
    description = fields.Char()
    rule_company_ids = fields.One2many('withholding.rules', 'withholding_cate_product')
    product_tmp_id = fields.One2many('product.template', 'withholding_category_id')


    


