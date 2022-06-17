from odoo import fields, models, api


class WithholdingType(models.Model):
    _name = 'withholding.type'
    _description = 'Withholding settings'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', 'Company')
    journal_id = fields.Many2one('account.journal', domain="[('type', '=', 'general')]")
    name = fields.Char()
    description = fields.Char()
    is_sale = fields.Boolean()
    use_part_taxpayer_type = fields.Boolean()
    use_company_taxpayer_type = fields.Boolean()
    use_part_ciiu = fields.Boolean()
    use_company_ciiu = fields.Boolean()
    use_part_city = fields.Boolean()
    use_company_city = fields.Boolean()
    use_withholding_Category = fields.Boolean()
    use_product_tax_category = fields.Boolean()
    rules_calc_ids = fields.One2many('withholding.calc', 'withholding_id', ondelete="cascade")
    rules_rules_ids = fields.One2many('withholding.rules', 'withholding_id', ondelete="cascade")
    account_move_withholding_p_ids = fields.One2many('account.move.withholding', 'type_withholding_purchase_id')
    account_move_withholding_s_ids = fields.One2many('account.move.withholding', 'type_withholding_sale_id')
    withholding_sequence_ids = fields.One2many('withholding.sequence', 'withholding_id', ondelete="cascade")
    use_sequence = fields.Boolean()


class WithholdingCalc(models.Model):
    _name = 'withholding.calc'
    _description = 'Withholding settings'

    company_id = fields.Many2one('res.company', 'Company')
    withholding_id = fields.Many2one('withholding.type', ' Withholding Type', ondelete="cascade")
    name = fields.Char()
    description = fields.Char()
    use_part_taxpayer_type = fields.Boolean(related='withholding_id.use_part_taxpayer_type', store=True)
    use_company_taxpayer_type = fields.Boolean(related='withholding_id.use_company_taxpayer_type', store=True)
    use_part_ciiu = fields.Boolean(related='withholding_id.use_part_ciiu', store=True)
    use_company_ciiu = fields.Boolean(related='withholding_id.use_company_ciiu', store=True)
    use_part_city = fields.Boolean(related='withholding_id.use_part_city', store=True)
    use_company_city = fields.Boolean(related='withholding_id.use_company_city', store=True)
    use_withholding_Category = fields.Boolean(related='withholding_id.use_withholding_Category', store=True)
    use_product_tax_category = fields.Boolean(related='withholding_id.use_product_tax_category', store=True)
    tax_base_id = fields.Many2one('account.tax', 'Tax', domain="[('is_withholding', '=', False), ('company_id', '=', company_id)]")
    tax_id = fields.Many2one('account.tax', 'Tax', domain="[('is_withholding', '=', True), ('company_id', '=', company_id)]")
    rules_ids = fields.One2many('withholding.rules', 'withholding_calc_id', ondelete="cascade")
    subtracting = fields.Float(default=0.0)
    base_type = fields.Selection(
        [
            ('L', 'Line'),
            ('T', 'Tax')
        ], default='T'
    )


class WithholdingRules(models.Model):
    _name = 'withholding.rules'
    _description = 'Withholding settings'

    company_id = fields.Many2one('res.company', 'Company')
    withholding_id = fields.Many2one('withholding.type', ' Withholding Type', ondelete="cascade")
    name = fields.Char()
    tax_payer_company = fields.Many2one('tax.payer.type', 'Tax Payer Company')
    tax_payer_partner = fields.Many2one('tax.payer.type', 'Tax Payer Partner')
    ciiu_company = fields.Many2one('ciiu', 'CIIU Company')
    ciiu_partner = fields.Many2one('ciiu', 'CIIU Partner')
    city_company = fields.Many2one('res.country.state', 'City Company')
    city_partner = fields.Many2one('res.country.state', 'City Partner')
    withholding_cate_product = fields.Many2one('withholding.category', 'Withholding Category')
    tax_group_id = fields.Many2one('account.tax.group', 'Group Tax')
    withholding_calc_id = fields.Many2one('withholding.calc', 'Withholding Calculation', ondelete="cascade")
    withholding_move_ids = fields.One2many('account.move.withholding', 'rules_id')
    use_part_taxpayer_type = fields.Boolean(related='withholding_calc_id.use_part_taxpayer_type', store=True)
    use_company_taxpayer_type = fields.Boolean(related='withholding_calc_id.use_company_taxpayer_type', store=True)
    use_part_ciiu = fields.Boolean(related='withholding_calc_id.use_part_ciiu', store=True)
    use_company_ciiu = fields.Boolean(related='withholding_calc_id.use_company_ciiu', store=True)
    use_part_city = fields.Boolean(related='withholding_calc_id.use_part_city', store=True)
    use_company_city = fields.Boolean(related='withholding_calc_id.use_company_city', store=True)
    use_withholding_Category = fields.Boolean(related='withholding_calc_id.use_withholding_Category', store=True)
    use_product_tax_category = fields.Boolean(related='withholding_calc_id.use_product_tax_category', store=True)

    @api.constrains('withholding_calc_id')
    def set_withholding(self):
        self.withholding_id = self.withholding_calc_id.withholding_id.id
