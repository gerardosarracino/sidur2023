# -*- coding: utf-8 -*-
from odoo import http
from jinja2 import Template


class GaleriaEnv(http.Controller):
    @http.route('/galeria_env/galeria_env/', auth='user')
    def index(self, **kw):
        plantilla = open('/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/galeria_env/controllers/index.html','r')
        id = kw.get('id')
        template = Template(plantilla.read())
        return template.render(
            id = id
        )

    @http.route('/galeria_env/galeria_informe/', auth='user')
    def index(self, **kw):
        plantilla = open('/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/galeria_env/controllers/index2.html','r')
        id = kw.get('id')
        template = Template(plantilla.read())
        return template.render(
            id = id
        )
#     @http.route('/galeria_env/galeria_env/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('galeria_env.listing', {
#             'root': '/galeria_env/galeria_env',
#             'objects': http.request.env['galeria_env.galeria_env'].search([]),
#         })

#     @http.route('/galeria_env/galeria_env/objects/<model("galeria_env.galeria_env"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('galeria_env.object', {
#             'object': obj
#         })