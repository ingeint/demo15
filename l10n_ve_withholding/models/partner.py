from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    ciiu_partner = fields.Many2one('ciiu', 'CIIU Partner')


class Company(models.Model):
    _inherit = 'res.company'

    ciiu_company = fields.Many2one('ciiu', 'CIIU Partner')
