# -*- coding: utf-8 -*-
{
    'name': "l10n_ve_identification",

    'summary': """
        Localization Venezuela for odoo""",

    'description': """
    Latam identification for Venezuela
    """,

    'author': "Orlando Curieles",
    'website': "https://www.ingeint.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'l10n_latam_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/latam_identification_type.xml',
        'views/tax_payer_type.xml',
        'views/latam_identification_type.xml',
        'views/partner.xml',
        'views/company.xml',
        'data/l10n_latam.identification.type.csv',
        'data/tax.payer.type.csv',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
