from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    generate_withholdings = fields.Boolean()
    


