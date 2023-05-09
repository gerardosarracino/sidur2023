# -*- coding: utf-8 -*-
from odoo import http

# class AutorizacionObra(http.Controller):
#     @http.route('/autorizacion_obra/autorizacion_obra/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/autorizacion_obra/autorizacion_obra/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('autorizacion_obra.listing', {
#             'root': '/autorizacion_obra/autorizacion_obra',
#             'objects': http.request.env['autorizacion_obra.autorizacion_obra'].search([]),
#         })

#     @http.route('/autorizacion_obra/autorizacion_obra/objects/<model("autorizacion_obra.autorizacion_obra"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('autorizacion_obra.object', {
#             'object': obj
#         })