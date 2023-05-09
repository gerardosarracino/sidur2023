# -*- coding: utf-8 -*-
from odoo import http

# class Auditorias(http.Controller):
#     @http.route('/auditorias/auditorias/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/auditorias/auditorias/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('auditorias.listing', {
#             'root': '/auditorias/auditorias',
#             'objects': http.request.env['auditorias.auditorias'].search([]),
#         })

#     @http.route('/auditorias/auditorias/objects/<model("auditorias.auditorias"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('auditorias.object', {
#             'object': obj
#         })