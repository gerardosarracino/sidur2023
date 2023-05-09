# -*- coding: utf-8 -*-
from odoo import http

# class Finiquito(http.Controller):
#     @http.route('/finiquito/finiquito/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/finiquito/finiquito/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('finiquito.listing', {
#             'root': '/finiquito/finiquito',
#             'objects': http.request.env['finiquito.finiquito'].search([]),
#         })

#     @http.route('/finiquito/finiquito/objects/<model("finiquito.finiquito"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('finiquito.object', {
#             'object': obj
#         })