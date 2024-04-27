from odoo import fields, models, api


class AccountingReport(models.AbstractModel):
    _inherit = 'account.accounting.report'
    _description = 'Accounting Report Helper'


    country_id = fields.Many2one('res.country')

