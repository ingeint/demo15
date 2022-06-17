# -*- coding: utf-8 -*-
{
    'name': "withholdings LVE",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jorge Pinero",
    'website': "http://www.ingeint.com",

    'category': 'accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'product', 'contacts', 'l10n_ve_identification'],

    # always loaded
    'data': [
        #'data/res_company.xml',
        #'data/journal.xml',
        #'data/categories_withholding.xml',
        #'data/rules_withholding.xml',
        'security/withholding_group.xml',
        'security/ir.model.access.csv',
        #'data/withholding.type.csv',
        #'data/withholding.calc.csv',
        #'data/withholding.rules.csv',
        'views/CIIU.xml',
        'views/type_withhouldings.xml',
        'views/withholding_category.xml',
        'views/withholding_sequence.xml',
        'views/product_template.xml',
        'views/tax_account.xml',
        'views/account_move.xml',
        'views/partner.xml',
        'views/company.xml',
        'views/account_journal.xml',
        'wizard/create_type_wh.xml',
        'views/menu.xml',
    ],
}
