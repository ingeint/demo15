from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Withholding(models.Model):
    _name = 'withholding.sequence'
    _description = 'Withholding Sequence'

    name = fields.Char(copy=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    ir_sequence = fields.Many2one('ir.sequence', copy=False)
    withholding_id = fields.Many2one('withholding.type')

    @api.constrains('company_id', 'ir_sequence')
    def validate_company(self):
        dist = bool(self.env['ir.module.module'].sudo().search([('name', '=', 'ing_accounting_distribution'), ('state', '=', 'installed')]))
        if dist:
            if self.accounting_by_tag:
                domain = [('company_id', '=', self.company_id.id),
                          ('accounting_tag_id', '=', self.accounting_tag_id.id),
                          ('id', '!=', self.id),
                          ('withholding_id', '=', self.withholding_id)
                          ]
            else:
                domain = [('company_id', '=', self.company_id.id),
                          ('withholding_id', '=', self.withholding_id),
                          ('id', '!=', self.id)]
        else:
            domain = [('company_id', '=', self.company_id.id),
                      ('withholding_id', '=', self.withholding_id),
                      ('id', '!=', self.id)]

        val_dist = self.search(domain)
        if val_dist:
            raise ValidationError(_('Duplicate Withholding Sequence!'))
