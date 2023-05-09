# -*- coding: utf-8 -*-
from odoo import http

# class Auditoria(http.Controller):
#     @http.route('/auditoria/auditoria/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auditoria/auditoria/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('auditoria.listing', {
#             'root': '/auditoria/auditoria',
#             'objects': http.request.env['auditoria.auditoria'].search([]),
#         })

#     @http.route('/auditoria/auditoria/objects/<model("auditoria.auditoria"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auditoria.object', {
#             'object': obj
#         })