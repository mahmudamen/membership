# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.tools.misc import format_date
import markupsafe
from markupsafe import Markup

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_country = True
    country_id = fields.Many2one('res.country')

    @api.model
    def get_html(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        # Prevent inconsistency between options and context.
        if options:
            self = self.with_context(self._set_context(options))
        else:
            options = line_id


        templates = self._get_templates()
        report_manager = self._get_report_manager(options)

        render_values = self._get_html_render_values(options, report_manager)
        if additional_context:
            return False #render_values.update(additional_context)

        # Create lines/headers.
        if line_id:
            headers = options['headers']
            lines = self._get_lines(options, line_id=line_id)
            template = templates['line_template']
        else:
            headers, lines = self._get_table(options)
            options['headers'] = headers
            template = templates['main_template']
        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        lines = self._format_lines_for_display(lines, options)

        render_values['lines'] = {'columns_header': headers, 'lines': lines}

        # Manage footnotes.
        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
            # we don't know all the visible lines.
            footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

        # Render.
        html = self.env.ref(template)._render(render_values)
        if self.env.context.get('print_mode', False):
            for k,v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(markupsafe.Markup('<div class="js_account_report_footnotes"></div>'), self.get_html_footnotes(footnotes_to_render))
        return html




    def _get_options(self, previous_options):
        # OVERRIDE
        options = super(AccountReport, self)._get_options(previous_options=previous_options)
        self._set_context(options)
        return options


    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        options = super(AccountReport, self)._set_context(options)
        options['filter_country'] = True
        return options

class AccountAgedPayable(models.Model):
    _inherit = 'account.aged.payable'


    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountAgedPayable, self)._get_options(previous_options=previous_options)
        options['filter_country'] = True
        return options

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        options = super(AccountAgedPayable, self)._set_context(options)
        options['filter_country'] = True
        return
    @api.model
    def _get_templates(self):
        options = self._get_options()
        if options['filter_country']:
            return self._get_templates_country()
        elif not options['filter_country']:
            return self._get_templates_partner()
    def _get_templates_partner(self):
        return {
                'main_template': 'account_reports.main_template',
                'main_table_header_template': 'account_reports.main_table_header',
                'line_template': 'account_reports.line_template',
                'footnotes_template': 'account_reports.footnotes_template',
                'search_template': 'account_reports.search_template',
                'line_caret_options': 'account_reports.line_caret_options',
        }
    def _get_templates_country(self):
        return {
            'main_template': 'account_reports_country.main_template',
            'main_table_header_template': 'account_reports.main_table_header',
            'line_template': 'account_reports.line_template',
            'footnotes_template': 'account_reports.footnotes_template',
            'search_template': 'account_reports.search_template',
            'line_caret_options': 'account_reports_country.line_caret_options',
        }
    def _get_hierarchy_details(self, options):
        if options['filter_country']:
            return self._get_hierarchy_details_country(options)
        elif not options['filter_country']:
            return self._get_hierarchy_details_partner(options)
    def _get_hierarchy_details_partner(self, options):
        return [
            self._hierarchy_level('partner_id', foldable=True, namespan=-7),
            self._hierarchy_level('id'),
        ]
    def _get_hierarchy_details_country(self, options):
        return [
            self._hierarchy_level('country_id', lazy=True, foldable=True, namespan=-1),
            self._hierarchy_level('partner_id', lazy=True, foldable=True, namespan= -7),
            self._hierarchy_level('id'),
        ]
class AccountAgedReceivable(models.Model):
    _inherit = 'account.aged.receivable'

    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountAgedReceivable, self)._get_options(previous_options=previous_options)
        options['filter_country'] = True
        return options

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        options = super(AccountAgedReceivable, self)._set_context(options)
        options['filter_country'] = True
        return options
    @api.model
    def _get_templates(self):
        options = self._get_options()
        if options['filter_country']:
            return self._get_templates_country()
        elif not options['filter_country']:
            return self._get_templates_partner()
    def _get_templates_partner(self):
        return {
                'main_template': 'account_reports.main_template',
                'main_table_header_template': 'account_reports.main_table_header',
                'line_template': 'account_reports.line_template',
                'footnotes_template': 'account_reports.footnotes_template',
                'search_template': 'account_reports.search_template',
                'line_caret_options': 'account_reports.line_caret_options',
        }
    def _get_templates_country(self):
        return {
                'main_template': 'account_reports_country.main_template',
                'main_table_header_template': 'account_reports.main_table_header',
                'line_template': 'account_reports_country.line_template',
                'footnotes_template': 'account_reports.footnotes_template',
                'search_template': 'account_reports.search_template',
                'line_caret_options': 'account_reports_country.line_caret_options',
        }

    def _get_hierarchy_details(self, options):
        if options['filter_country']:
            return self._get_hierarchy_details_country(options)
        elif not options['filter_country']:
            return self._get_hierarchy_details_partner(options)
    def _get_hierarchy_details_partner(self, options):
        return [
            self._hierarchy_level('partner_id',lazy=True, foldable=True, namespan=-1),
            self._hierarchy_level('id'),
        ]
    def _get_hierarchy_details_country(self, options):
        return [

            self._hierarchy_level('country_id',lazy=True, foldable=True, namespan=-1),
            self._hierarchy_level('partner_id',lazy=True, foldable=True,namespan= -7),
            self._hierarchy_level('id'),


        ]

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    country_id = fields.Many2one('res.country',related='partner_id.country_id', store=True)

class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"
    _description = "Aged Partner Balances"

    def _format_country_id_line(self, res, value_dict, options):
        res['name'] = value_dict['country_id'][1] if value_dict['country_id'] else _('Unknown Country')

    def _format_partner_id_line(self, res, value_dict, options):
        res['name'] = value_dict['partner_name'][:128] if value_dict['partner_name'] else _('Unknown Partner')
