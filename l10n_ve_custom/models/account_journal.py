from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    have_cn_sequence = fields.Boolean(default=False, copy=False)
    sequence_no_control_id = fields.Many2one('ir.sequence', copy=False)



