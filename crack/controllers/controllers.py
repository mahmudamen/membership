# -*- coding: utf-8 -*-
from odoo import http

# class Crack(http.Controller):
#     @http.route('/crack/crack/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crack/crack/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crack.listing', {
#             'root': '/crack/crack',
#             'objects': http.request.env['crack.crack'].search([]),
#         })

#     @http.route('/crack/crack/objects/<model("crack.crack"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crack.object', {
#             'object': obj
#         })