# -*- coding: utf-8 -*-
# Copyright 2023 IZI PT Solusi Usaha Mudah
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# noinspection PyUnresolvedReferences,SpellCheckingInspection
{
    'name': "Spreadsheet Data Library Connector",
    'summary': """
        "Spreadsheet Data Library Connector" enables seamless data import from CSV, Excel, and Google Spreadsheets, 
        streamlining data integration in Odoo.""",
    "category": "Reporting",
    "version": "15.0.0.1.0",
    "development_status": "Alpha",  # Options: Alpha|Beta|Production/Stable|Mature
    "auto_install": False,
    "installable": True,
    "application": False,
    "author": "IZI PT Solusi Usaha Mudah",
    "support": "admin@iziapp.id",
    "website": "https://www.iziapp.id",
    "license": "OPL-1",
    "images": [
        'static/description/banner.jpg'
    ],

    "price": 0.00,
    "currency": "USD",

    # any module necessary for this one to work correctly
    'depends': ['izi_data', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/example.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
