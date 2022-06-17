from odoo import fields, models, api, _


class ModelName(models.TransientModel):
    _name = 'create.type.wh'
    _description = 'Create type Withholding'

    type_base_id = fields.Many2one('withholding.type')
    company_to_ids = fields.Many2many('res.company')
    company_id = fields.Many2one('res.company')

    @api.onchange('type_base_id')
    def set_company(self):
        if self.type_base_id:
            self.write({'company_id': self.type_base_id.company_id.id,
                        'company_to_ids': False})
        else:
            self.write({'company_id': False,
                        'company_to_ids': False})

    def create_val(self):
        if self.type_base_id:
            for co in self.company_to_ids:
                type_whh = self.env['withholding.type'].sudo().search(
                    [('company_id', '=', co.id), ('name', '=', self.type_base_id.name)])
                if not type_whh:
                    journal_env = self.env['account.journal']
                    journal = journal_env.sudo().search(
                        [('name', '=', self.type_base_id.journal_id.name), ('company_id', '=', co.id)])
                    if not journal:
                        journal = journal_env.create({
                            'name': self.type_base_id.journal_id.name,
                            'type': 'general',
                            'company_id': co.id,
                            'code': 'wh'
                        })

                    type_wh = self.env['withholding.type'].sudo().create({'name': self.type_base_id.name,
                                                                          'company_id': co.id,
                                                                          'journal_id': journal.id,
                                                                          'description': self.type_base_id.description,
                                                                          'is_sale': self.type_base_id.is_sale,
                                                                          'use_part_taxpayer_type': self.type_base_id.use_part_taxpayer_type,
                                                                          'use_company_taxpayer_type': self.type_base_id.use_company_taxpayer_type,
                                                                          'use_part_ciiu': self.type_base_id.use_part_ciiu,
                                                                          'use_company_ciiu': self.type_base_id.use_company_ciiu,
                                                                          'use_part_city': self.type_base_id.use_part_city,
                                                                          'use_company_city': self.type_base_id.use_company_city,
                                                                          'use_withholding_Category': self.type_base_id.use_withholding_Category,
                                                                          'use_product_tax_category': self.type_base_id.use_product_tax_category
                                                                          })
                    for cal in self.type_base_id.rules_calc_ids:
                        tax_base = cal.env['account.tax'].sudo().search(
                            [('name', '=', cal.tax_base_id.name), ('company_id', '=', co.id)])

                        tax_id = cal.env['account.tax'].sudo().search(
                            [('name', '=', cal.tax_id.name), ('company_id', '=', co.id)])

                        cal_val = cal.env['withholding.calc'].sudo().create({'company_id': co.id,
                                                                             'withholding_id': type_wh.id,
                                                                             'name': cal.name,
                                                                             'description': cal.name,
                                                                             'tax_id': tax_id.id,
                                                                             'tax_base_id': tax_base.id})
                        for rule in cal.rules_ids:
                            rule.env['withholding.rules'].sudo().create({'company_id': co.id,
                                                                         'withholding_id': type_wh.id,
                                                                         'name': rule.name,
                                                                         'tax_payer_company': rule.tax_payer_company.id,
                                                                         'tax_payer_partner': rule.tax_payer_partner.id,
                                                                         'ciiu_company': rule.ciiu_company.id,
                                                                         'ciiu_partner': rule.ciiu_partner.id,
                                                                         'city_company': rule.city_company.id,
                                                                         'city_partner': rule.city_partner.id,
                                                                         'withholding_cate_product': rule.withholding_cate_product.id,
                                                                         'tax_group_id': rule.tax_group_id.id,
                                                                         'withholding_calc_id': cal_val.id})
