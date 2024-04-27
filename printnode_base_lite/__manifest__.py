# Copyright 2023 VentorTech OU
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Direct Print Lite',
    'summary': """
        Print any reports directly to any local, Wi-Fi or Bluetooth printer
        without downloading PDF or ZPL!
    """,
    'version': '15.0.1.0.0',
    'category': 'Tools',
    "images": ["static/description/images/banner.gif"],
    'author': 'VentorTech',
    'website': 'https://ventor.tech',
    'support': 'support@ventor.tech',
    'license': 'OPL-1',
    'price': 0.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'stock',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Initial Data
        'data/ir_cron_data.xml',
        'data/ir_config_parameter_data.xml',
        # Root menus
        'views/printnode_menus.xml',
        # Wizards
        'wizard/printnode_installer_wizard.xml',
        'wizard/printnode_upgrade_wizard.xml',
        # Model Views
        'views/printnode_account_views.xml',
        'views/printnode_computer_views.xml',
        'views/printnode_printer_views.xml',
        'views/printnode_action_button_views.xml',
        'views/printnode_scenario_views.xml',
        'views/printnode_report_policy_views.xml',
        'views/printnode_rule_views.xml',
        'views/printnode_workstation_views.xml',
        'views/shipping_label_views.xml',
        'views/stock_picking_views.xml',
        'views/printnode_scales_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'printnode_base_lite/static/src/css/status_menu.css',
            'printnode_base_lite/static/src/js/status_menu.js',
            'printnode_base_lite/static/src/js/download_menu.js',
            'printnode_base_lite/static/src/js/action_service.js',
        ],
        'web.assets_qweb': [
            'printnode_base_lite/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'application': True,
}
