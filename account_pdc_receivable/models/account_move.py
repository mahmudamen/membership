from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    # is_pdc_receivable_entry = fields.Boolean(string='Is PDC Receivable Entry', readonly=True, store=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # is_pdc_receivable_entry = fields.Boolean(string='Is PDC Receivable Entry', readonly=True, store=True)
