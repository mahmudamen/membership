{
    'name': 'Sale Subscription',
    'version': '15.0.1.0',
    'summary': 'This module enables subscription for Products',
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com",
    'category': 'Sales',
    'depends': [
        'sale','product','stock'
    ],
    'data': [

        "security/ir.model.access.csv",
        "views/subscription_views.xml",
        'views/product_views.xml',
        "views/sale_views.xml",
        "views/ir_cron.xml",
        "views/close_reason.xml",
        "wizard/close_reason_wizard.xml"
    ],
    'license':"LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/banner.png'],
}
