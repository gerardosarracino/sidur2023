# -*- coding: utf-8 -*-
from odoo import http

# class Extra-addons/curso-odoo12/library(http.Controller):
#     @http.route('/extra-addons/curso-odoo12/library/extra-addons/curso-odoo12/library/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/extra-addons/curso-odoo12/library/extra-addons/curso-odoo12/library/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('extra-addons/curso-odoo12/library.listing', {
#             'root': '/extra-addons/curso-odoo12/library/extra-addons/curso-odoo12/library',
#             'objects': http.request.env['extra-addons/curso-odoo12/library.extra-addons/curso-odoo12/library'].search([]),
#         })

#     @http.route('/extra-addons/curso-odoo12/library/extra-addons/curso-odoo12/library/objects/<model("extra-addons/curso-odoo12/library.extra-addons/curso-odoo12/library"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('extra-addons/curso-odoo12/library.object', {
#             'object': obj
#         })