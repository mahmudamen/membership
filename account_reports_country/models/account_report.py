from odoo import fields, models, api
import markupsafe
from markupsafe import Markup


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    country_all_filter = fields.Boolean('Show Group By Country', help='display the Groub By Country options in report')

    @property
    def filter_country(self):
        if self.country_all_filter:
            return True
        return super().filter_country