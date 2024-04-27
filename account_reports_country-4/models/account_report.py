from odoo import fields, models, api
import markupsafe
from markupsafe import Markup


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    country_all_filter = fields.Boolean('Show Group By Country', help='display the Groub By Country options in report')

    @property
    def filter_country(self):
        if self.country_all_filter:
            return False
        return super().filter_country

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        options = super(ReportAccountFinancialReport, self)._set_context(options)
        options['filter_country'] = True
        return options