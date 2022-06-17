from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date, get_lang
from datetime import date
from ..utils import utils

from json import dumps
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_total_withholdings(self):
        results = self.env['account.move.withholding'].read_group([('move_id', 'in', self.ids)], ['move_id'],
                                                                  ['move_id'])
        dic = {}
        for x in results: dic[x['move_id'][0]] = x['move_id_count']
        for record in self: record['count_withholding'] = dic.get(record.id, 0)

    draft = fields.Boolean(default=False, copy=False)
    withholding_ids = fields.One2many('account.move.withholding', 'move_id')
    withholding_processed = fields.Boolean(copy=False)
    withholding_generate = fields.Boolean(copy=False)
    count_withholding = fields.Float(compute=get_total_withholdings)
    withholding_number = fields.Char(copy=False)
    move_wh_id = fields.Many2one('account.move', copy=False)

    @api.onchange('no_withholding_sale')
    def create_number_wh(self):
        if self.no_withholding_sale:
            no_withholding = self.no_withholding_sale.replace(" ", "")
            if len(no_withholding) != 17:
                if no_withholding.isdigit() and len(no_withholding) == 15:
                    first = self.no_withholding_sale[0:3] + '-'
                    two = self.no_withholding_sale[3:6] + '-'
                    three = self.no_withholding_sale[6:17]
                    self.no_withholding_sale = str(first) + str(two) + str(three)
                else:
                    self.write({'no_withholding_sale': False})
                    message = _('Error the document number is incorrect')
                    mess = {'title': _('Warning!'),
                            'message': message
                            }
                    return {'warning': mess}

    @api.onchange('no_withholding_aut')
    def validate_withholding_aut(self):
        if self.no_withholding_aut:
            withholding_aut = self.no_withholding_aut.replace(" ", "")
            if len(withholding_aut) != 10 and len(withholding_aut) != 49:
                self.write({'no_withholding_aut': False})
                message = _('Error the code is not valid')
                mess = {'title': _('Warning!'),
                        'message': message
                        }
                return {'warning': mess}

    def generate_withholdings(self):
        if self.journal_id.generate_withholdings:
            iso_trx = False
            if self.move_type != 'in_invoice':
                iso_trx = True

            if self.move_type == 'in_invoice':
                self.withholding_generate = True

            type_w = self.env['withholding.type'].search(
                [("is_sale", '=', iso_trx), ("company_id", '=', self.company_id.id)])

            self.withholding_ids.unlink()

            type_wh = 'select id from withholding_rules where 1 = 1'
            result_sql = []
            for with_move in type_w:
                if with_move.use_company_taxpayer_type:
                    id_value_c = 0
                    if self.company_id.tax_payer_type_id.id:
                        id_value_c = self.company_id.tax_payer_type_id.id
                    type_wh += ' and tax_payer_company = ' + str(id_value_c)
                if with_move.use_part_taxpayer_type:
                    id_value_p = 0
                    if self.partner_id.tax_payer_type_id.id:
                        id_value_p = self.partner_id.tax_payer_type_id.id
                    type_wh += ' and tax_payer_partner = ' + str(id_value_p)
                if with_move.use_company_ciiu:
                    id_value_cic = 0
                    if self.company_id.ciiu_company.id:
                        id_value_cic = self.company_id.ciiu_company.id
                    type_wh += ' and ciiu_company = ' + str(id_value_cic)
                if with_move.use_part_ciiu:
                    id_value_cip = 0
                    if self.self.partner_id.ciiu_partner.id:
                        id_value_cip = self.partner_id.ciiu_partner.id
                    type_wh += ' and ciiu_partner = ' + str(id_value_cip)
                if with_move.use_company_city:
                    id_value_cc = 0
                    if self.company_id.state_id.id:
                        id_value_cc = self.company_id.state_id.id
                    type_wh += ' and city_company = ' + str(id_value_cc)
                if with_move.use_part_city:
                    id_value_cp = 0
                    if self.partner_id.state_id.id:
                        id_value_cp = self.partner_id.state_id.id
                    type_wh += ' and city_partner = ' + str(id_value_cp)
                if with_move.use_withholding_Category:
                    self._cr.execute(
                        'SELECT DISTINCT COALESCE (pl.withholding_category_id,0) '
                        ' from account_move_line aml '
                        '    join product_product pp on aml.product_id = pp.id '
                        '    join product_template pl on pp.product_tmpl_id = pl.id '
                        ' where aml.product_id notnull '
                        ' and aml.move_id = %s',
                        [self.id])
                    value = self._cr.fetchall()
                    id_value_wpc = []
                    if value:
                        for sqls in value:
                            id_value_wpc += [sqls[0]]
                        type_wh += ' and withholding_cate_product in ' + str(id_value_wpc).replace('[', '(').replace(
                            ']',
                            ')')
                if with_move.use_product_tax_category:
                    self._cr.execute(
                        'SELECT DISTINCT COALESCE (pl.tax_group_id,0,0) '
                        ' from account_move_line aml '
                        '    join product_product pp on aml.product_id = pp.id '
                        '    join product_template pl on pp.product_tmpl_id = pl.id '
                        ' where aml.product_id notnull '
                        ' and aml.move_id = %s',
                        [self.id])
                    value = self._cr.fetchall()
                    id_value_wp = []
                    if value:
                        for sqls in value:
                            id_value_wp += [sqls[0]]
                        type_wh += ' and tax_group_id in ' + str(id_value_wp).replace('[', '(').replace(']', ')')

                type_wh_r = str('select id from withholding_rules where 1 = 1')
                if type_wh != type_wh_r:
                    type_wh += ' and withholding_id = ' + str(with_move.id)
                    self._cr.execute(str(type_wh))
                    result_sql += self._cr.fetchall()
                    type_wh = 'select id from withholding_rules where 1 = 1 '

            for rules_with in result_sql:
                sum_cate_with_tax = 0
                sum_cate_tax = 0
                sum_cate_with = 0
                sum_lines_tax = 0
                sum_lines_total = 0
                rules_calc = self.env['withholding.rules'].search([('id', '=', rules_with[0])])
                if rules_calc.withholding_id.use_withholding_Category and rules_calc.withholding_id.use_product_tax_category:
                    self._cr.execute(
                        ' SELECT sum(COALESCE (aml.price_subtotal )) '
                        ' from account_move_line aml '
                        '    join product_product pp on aml.product_id = pp.id '
                        '    join product_template pl on pp.product_tmpl_id = pl.id '
                        ' where aml.product_id notnull '
                        ' and pl.withholding_category_id = %s'
                        ' and pl.tax_group_id = %s'
                        ' and aml.move_id = %s',
                        [rules_calc.withholding_cate_company.id, rules_calc.tax_group_id.id, self.id])
                    value = self._cr.fetchall()
                    for sqls in value:
                        sum_cate_with_tax += sqls[0]

                elif rules_calc.withholding_id.use_withholding_Category:
                    self._cr.execute(
                        ' SELECT sum(COALESCE (aml.price_subtotal )) '
                        ' from account_move_line aml '
                        '    join product_product pp on aml.product_id = pp.id '
                        '    join product_template pl on pp.product_tmpl_id = pl.id '
                        ' where aml.product_id notnull '
                        ' and pl.withholding_category_id = %s'
                        ' and aml.move_id = %s',
                        [rules_calc.withholding_cate_product.id, self.id])
                    value = self._cr.fetchall()
                    for sqls in value:
                        sum_cate_with += sqls[0]

                elif rules_calc.withholding_id.use_product_tax_category:
                    self._cr.execute(
                        ' SELECT sum(COALESCE (aml.price_subtotal )) '
                        ' from account_move_line aml '
                        '    join product_product pp on aml.product_id = pp.id '
                        '    join product_template pl on pp.product_tmpl_id = pl.id '
                        ' where aml.product_id notnull '
                        ' and pl.tax_group_id = %s'
                        ' and aml.move_id = %s',
                        [rules_calc.tax_group_id.id, self.id])
                    value = self._cr.fetchall()
                    for sqls in value:
                        sum_cate_tax += sqls[0]

                elif rules_calc.withholding_calc_id.base_type == 'T':
                    lines = self.env['account.move.line'].search([('move_id', '=', self.id), (
                        'tax_line_id', '=', rules_calc.withholding_calc_id.tax_base_id.id)])
                    for record_lines in lines:
                        sum_lines_tax += record_lines.price_subtotal

                elif rules_calc.withholding_calc_id.base_type == 'L':
                    lines_total = self.env['account.move.line'].search(
                        [('move_id', '=', self.id), ('product_id', '!=', False)])
                    for record_lines_total in lines_total:
                        sum_lines_total += record_lines_total.price_subtotal

                total_cal = sum_cate_with_tax + sum_cate_tax + sum_cate_with + sum_lines_tax + sum_lines_total

                validation = False
                if total_cal == 0 and rules_calc.withholding_calc_id.tax_base_id.amount == 0 or total_cal > 0:
                    validation = True

                if validation:
                    invoice_withholding = self.env['account.move.withholding']
                    wh = invoice_withholding.create_withholding(self.company_id.id,
                                                                self.id,
                                                                rules_calc.withholding_id.id,
                                                                rules_calc.withholding_id.id,
                                                                rules_calc.withholding_calc_id.tax_id.id,
                                                                total_cal,
                                                                rules_calc.id,
                                                                self.name,
                                                                self.invoice_date,
                                                                self.date,
                                                                self.move_type)
                    wh.set_tax_percent()

    def action_post(self):
        self.validate_transaction()
        self.validate_wh()
        res = super(AccountMove, self).action_post()
        if self.move_type == 'in_invoice':
            utils.process_withholding(self)
            self.withholding_processed = True
            for wh in self.withholding_ids:
                wh.wh_processed = True
        return res

    def validate_wh(self):
        if self.journal_id.generate_withholdings and self.move_type == 'in_invoice':
            if not self.withholding_generate:
                raise ValidationError(
                    _('you must generate retentions to be able to publish the document'))

    def validate_transaction(self):
        if self.date > date.today():
            raise UserError('You cannot process a document with a date greater than the current one')

    def generate_payment(self):
        utils.process_withholding(self)
        if self.move_wh_id:
            self.withholding_processed = True
            for wh in self.withholding_ids:
                wh.wh_processed = True

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        self.draft = True
        cr = self._cr
        if self.move_wh_id.id:
            cr.execute('delete from account_move where id = %s', [self.move_wh_id.id])
        return res

    def cancel_wh_sale(self):
        if self.state == 'posted' and self.move_wh_id:
            self.move_wh_id.button_draft()
            self._cr.execute('delete from account_move where id = %s', [self.move_wh_id.id])
            self.withholding_processed = False
            self.withholding_generate = False
            for wh_record in self.withholding_ids:
                wh_record.wh_processed = False
                wh_record.unlink()
