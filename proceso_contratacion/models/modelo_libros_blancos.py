# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.odoo import api


class LibrosBlancos(models.Model):
    _name = 'libros.blancos'
    _rec_name = 'contrato'

    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Contrato', store=True)

    # ELEMENTOS PARA LA VISTA INFORMATIVOS
    nombre_obra = fields.Text(string="Obra", related="contrato.name")
    contratista = fields.Many2one('contratista.contratista', related="contrato.contratista")
    radio_adj_lic = [('1', "Licitación"), ('2', "Adjudicación")]
    tipo_contrato = fields.Selection(radio_adj_lic, string="Tipo de Contrato", store=True, related="contrato.tipo_contrato")

    tabla_libros_blancos = fields.Many2many('expediente.libros_blancos', string='Revision de Expedientes', store=True)
    porcentaje_existencia = fields.Float(string="% Existencia", store=True)

    programa_inversion = fields.Many2one('generales.programas_inversion', string="Programa de Inversion")
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra", )
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", )

    @api.multi
    @api.onchange('tabla_libros_blancos')
    def onchange_method(self):
        if not self.tabla_libros_blancos:
            pass
        else:
            count_existencia = 0
            count_aplica = 0
            for i in self.tabla_libros_blancos:
                if i.existe == 'Si':
                    count_existencia += 1
                if i.aplica == 'Si':
                    count_aplica += 1
            self.porcentaje_existencia = (count_existencia / count_aplica) * 100

    reviso_expediente = fields.Boolean('Revisado')
    verificado_expediente = fields.Boolean('Verificado')
    fecha_revisado_exp = fields.Date(string="Fecha de Revisado", required=False, )
    fecha_verificado_exp = fields.Date(string="Fecha de Verificado", required=False, )
    comentarios_expediente = fields.Text(string="Comentario", required=False, )
    responsable_revision_exp = fields.Many2one('res.users', string='Responsable')  # compute="user_admin"