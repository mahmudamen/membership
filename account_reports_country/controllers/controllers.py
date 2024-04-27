# -*- coding: utf-8 -*-
# from odoo import http


# class ItsysMediatechFollowupTags(http.Controller):
#     @http.route('/account_reports_country/account_reports_country', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reports_country/account_reports_country/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reports_country.listing', {
#             'root': '/account_reports_country/account_reports_country',
#             'objects': http.request.env['account_reports_country.account_reports_country'].search([]),
#         })

#     @http.route('/account_reports_country/account_reports_country/objects/<model("account_reports_country.account_reports_country"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reports_country.object', {
#             'object': obj
#         })
