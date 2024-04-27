{
    'name': 'Account PDC Receivable Payment',
    'summary': 'Allow use PDC',
    'author': 'Plennix',
    'website': 'https://www.plennix.com/',
    'version': '15.0.1.2.2',
    'category': 'Accounting/Accounting',
    'license': 'OPL-1',
    'depends': ['account', 'account_pdc'],

    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
