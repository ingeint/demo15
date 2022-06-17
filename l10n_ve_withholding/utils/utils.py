from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


def process_withholding(self):
    lines = []
    if self.journal_id.generate_withholdings:
        if self.withholding_ids:
            amount_lines = 0
            currency_factor = self.currency_id.decimal_places
            journal_id = 0

            """" Evaluate values in wh """
            if self.amount_residual != 0:
                for withholding in self.withholding_ids:
                    if withholding.tax_withholding_id:
                        amount_withholding = withholding.tax_total
                        if withholding.tax_total < 0:
                            amount_withholding = withholding.tax_total * -1
                        if amount_withholding <= self.amount_total and amount_withholding <= self.amount_residual:
                            if self.move_type == 'out_invoice':
                                for rep in withholding.tax_withholding_id.invoice_repartition_line_ids:
                                    if rep.repartition_type == 'tax':
                                        amount = round(((amount_withholding * rep.factor_percent) / 100), currency_factor)
                                        debit = get_debit_value(_('CxC Withholding'),
                                                                rep.account_id.id,
                                                                self.date,
                                                                False,
                                                                amount)
                                        amount_lines += amount
                                        lines.append(debit)
                            elif self.move_type == 'in_invoice':
                                for rep in withholding.tax_withholding_id.invoice_repartition_line_ids:
                                    if rep.repartition_type == 'tax':
                                        amount = round(((amount_withholding * rep.factor_percent) / 100), currency_factor)
                                        debit = get_credit_value(_('CxP Withholding'),
                                                                 rep.account_id.id,
                                                                 self.date,
                                                                 False,
                                                                 amount)
                                        amount_lines += amount
                                        lines.append(debit)
                            journal_id = withholding.type_withholding_sale_id.journal_id.id if withholding.type_withholding_sale_id else withholding.type_withholding_purchase_id.journal_id.id
                            use_sequence = withholding.type_withholding_sale_id.use_sequence if withholding.type_withholding_sale_id else withholding.type_withholding_purchase_id.use_sequence
                            withholding_type = withholding.type_withholding_sale_id if withholding.type_withholding_sale_id else withholding.type_withholding_purchase_id
                            if use_sequence:
                                set_wh_sequence(withholding_type, withholding)
                        else:
                            raise ValidationError(
                                _('The total amount of withholding cannot be greater than the invoice value'))
                    else:
                        raise ValidationError(
                            _('You must set up a Tax in the type of retention'))
            else:
                raise ValidationError(_('You cannot generate retentions to a fully paid document'))

            """ Counterpart of securities evaluated by purchase and sale """
            if self.move_type == 'out_invoice':
                msg = _('CxC Withholding')
                credit_move_line = get_credit_value(msg,
                                                    self.partner_id.property_account_receivable_id.id,
                                                    self.date,
                                                    self.partner_id.id,
                                                    round(amount_lines, currency_factor))
                lines.append(credit_move_line)

            elif self.move_type == 'in_invoice':
                msg = _('CxP Withholding')
                debit_move_line = get_debit_value(msg,
                                                  self.partner_id.property_account_payable_id.id,
                                                  self.date,
                                                  self.partner_id.id,
                                                  round(amount_lines, currency_factor))
                lines.append(debit_move_line)

            distribute_account(self, msg, journal_id, lines)


def set_wh_sequence(self, wh):
    """Set wh Sequence"""
    dist = bool(self.env['ir.module.module'].sudo().search(
        [('name', '=', 'ing_accounting_distribution'), ('state', '=', 'installed')]))
    if dist:
        if self.accounting_by_tag:
            domain = [('company_id', '=', self.company_id.id),
                      ('accounting_tag_id', '=', self.accounting_tag_id.id),
                      ('withholding_id', '=', self.id)]
        else:
            domain = [('company_id', '=', self.company_id.id),
                      ('withholding_id', '=', self.id)]
    else:
        domain = [('company_id', '=', self.company_id.id),
                  ('withholding_id', '=', self.id)]

    sequence = self.env['withholding.sequence'].sudo().search(domain, limit=1)
    if not sequence:
        raise UserError(_('You must configure a Withholding sequence'))
    wh.document_no = sequence.sudo().ir_sequence.next_by_id()


def distribute_account(self, msg, journal_id, lines):
    line_ids_values = []
    if lines:
        dist = bool(self.env['ir.module.module'].sudo().search(
            [('name', '=', 'ing_accounting_distribution'), ('state', '=', 'installed')]))
        if dist:
            if self.env.company.accounting_by_tag:
                val = {
                    'ref': msg,
                    'date': self.date,
                    'move_type': 'entry',
                    'journal_id': journal_id,
                    'accounting_tag_id': self.accounting_tag_id.id
                }
            else:
                val = {
                    'ref': msg,
                    'date': self.date,
                    'move_type': 'entry',
                    'journal_id': journal_id,
                }
        else:
            val = {
                'ref': msg,
                'date': self.date,
                'move_type': 'entry',
                'journal_id': journal_id,
            }

        current_move = self.env['account.move'].create(val)
        line_ids_values += [(0, 0, value) for value in lines]
        current_move.write({'line_ids': line_ids_values})
        self.write({'move_wh_id': current_move.id})
        current_move.action_post()
        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        lines_current = current_move.line_ids.filtered_domain(domain)
        lines_invoice = self.line_ids.filtered_domain(domain)
        for payment, lines in zip(lines_current, lines_invoice):
            if payment.move_id.state != 'posted':
                continue

            (payment + lines) \
                .filtered_domain([('account_id', '=', lines.account_id.id), ('reconciled', '=', False)]) \
                .reconcile()


def get_debit_value(msg, account_debit, date, partner_debit_id, amount):
    debit_move_line = {
        'name': msg,
        'account_id': account_debit,
        'date_maturity': date,
        'credit': 0,
        'partner_id': partner_debit_id,
        'debit': amount
    }
    return debit_move_line


def get_credit_value(msg, account_credit, date, partner_debit_id, amount):
    account_debit = {
        'name': msg,
        'account_id': account_credit,
        'date_maturity': date,
        'credit': amount,
        'partner_id': partner_debit_id,
        'debit': 0
    }
    return account_debit
