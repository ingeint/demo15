from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_no = fields.Char(copy=False)
    control_number = fields.Char(copy=False)

    def action_post(self):
        if self.journal_id.have_cn_sequence and self.move_type == 'out_invoice':
            if not self.control_number:
                sequence = self.journal_id.sequence_no_control_id.next_by_id()
                if not sequence:
                    raise UserError(_('You Must configure a sequence for the document'))
                self.control_number = sequence
        res = super(AccountMove, self).action_post()
        return res

    _sql_constraints = [('invoice_p_unique', 'unique(invoice_no,partner_id)', 'This invoice is already registered')]

