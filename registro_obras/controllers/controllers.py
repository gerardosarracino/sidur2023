# -*- coding: utf-8 -*-
from odoo import http

# class RegistroObras(http.Controller):
#     @http.route('/registro_obras/registro_obras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/registro_obras/registro_obras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('registro_obras.listing', {
#             'root': '/registro_obras/registro_obras',
#             'objects': http.request.env['registro_obras.registro_obras'].search([]),
#         })

#     @http.route('/registro_obras/registro_obras/objects/<model("registro_obras.registro_obras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('registro_obras.object', {
#             'object': obj
#         })