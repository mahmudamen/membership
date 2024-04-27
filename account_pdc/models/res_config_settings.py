from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hand_over_pdc_email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template for Hand Over PDC',
        domain="[('model', '=', 'account.hand.over.pdc')]",
        config_parameter='account_pdc.default_notify_hand_over_template',
        help="Email sent to the users to approve."
    )
    hand_over_pdc_reject_email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='Email Template for Hand Over Reject PDC',
        domain="[('model', '=', 'account.hand.over.pdc')]",
        config_parameter='account_pdc.default_notify_hand_over_reject_template',
        help="Email sent to the users to approve."
    )
