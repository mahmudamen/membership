# -*- coding: utf-8 -*-
{
    'name': "account_reports_country",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/report_financial.xml',
        'views/search_template_view.xml',
    ],
    "assets": {
        "web.assets_backend": [
            'account_reports_country/static/src/js/account_reports.js',
        ],
        "web.report_assets_common": [

        ],
        "web.assets_qweb": [

        ],
    },



}
