# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime, date, time, timedelta
import calendar
from jinja2 import Template


class Documentos(http.Controller):
    # @http.route('/documento/licitaciones/<id>', type='http', auth='public')
    # def index(self,id):
    #     plantilla = http.request.env['plantillas.plantillas']
    #     doc = plantilla.sudo().search([('id','=',id)])
    #     prs = Presentation('/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/powerpoint/static/plantilla.pptx')

    #     prs.save('/tmp/test.pptx')
    #     f = open('/tmp/test.pptx', mode="rb")
    #     return http.request.make_response(f.read(),
    #                                       [('Content-Type', 'application/octet-stream'),
    #                                        ('Content-Disposition',
    #                                         'attachment; filename="{}"'.format('sidur.pptx'))
    #                                        ])

    @http.route('/docx/<tipo_documento>/id/<id>', type='http', auth='public')
    def indexDos(self,tipo_documento,id):
        busca_id_tipo_docuento = http.request.env['plantillas.documento'].sudo().search([('name','=',tipo_documento)])
        plantilla = http.request.env['plantillas.plantillas']
        doc = plantilla.sudo().search([('tipo_documento','=',busca_id_tipo_docuento[0].id)]) #el 1 corresponde a la categoria de invitaciones
        #doc = plantilla.sudo().search([()])
        plantilla = open('/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/documentos/controllers/template/resultado.html','r')
        template = Template(plantilla.read())
        return template.render(
            data = doc,
            id = id
            )

    @http.route('/docx/listado', type='http', auth='public')
    def indexTres(self):
        plantilla = http.request.env['plantillas.plantillas']
        #doc = plantilla.sudo().search([('tipo_documento','=','')])
        doc = plantilla.sudo().search([])
        plantilla = open('/usr/lib/python3/dist-packages/odoo/odoo-extra-addons/documentos/controllers/template/resultado.html','r')
        template = Template(plantilla.read())
        return template.render(
            data = doc
            )
            