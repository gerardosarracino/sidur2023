# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class AdjudicacionDirecta(models.Model):
    _name = "proceso.adjudicacion_directa"
    _rec_name = "numerocontrato"

    id_sideop_adjudicacion = fields.Integer('ID SIDEOP')
    id_sideop_partida = fields.Integer('ID SIDEOP part')

    # CAMPO BOOLEAN PARA VERIFICAR SI YA SE CONTRATO ESTA ADJUDICACION
    contratado = fields.Integer(string="", store=True)

    #  HACER LOS FILTROS DE RELACION DE PROGRAMAS DE INVERSION CON OBRAS PROGRAMADAS(partidas)
    name = fields.Text(string="Descripción/Meta", required=True)
    programas_inversion_adjudicacion = fields.Many2one('generales.programas_inversion', 'name', required=True)
    # /// Partidas
    programar_obra_adjudicacion = fields.Many2many("partidas.adjudicacion", string="Partida(s):", store=True)

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio",
                                related="programar_obra_adjudicacion.obra.obra_planeada.ejercicio")
                                
    iva = fields.Float(string="I.V.A", compute="BuscarIva")

    importe_adjudicacion = fields.Float(string="Importe",)

    numerocontrato = fields.Char(string="Numero Contrato", required=True)

    fechaadjudicacion = fields.Date(string="Fecha de Adjudicación", required=True )
    dictamen = fields.Char(string="Dictamen", )
    select = [('1', 'Federal'), ('2', 'Estatal')]
    normatividad = fields.Selection(select, string="Normatividad", default="1", )
    anticipoinicio = fields.Float(string="Anticipo Inicio %")
    anticipomaterial = fields.Float(string="Anticipo Material %")
    fechainicio = fields.Date(string="Fecha de Inicio", default=fields.Date.today())
    fechatermino = fields.Date(string="Fecha termino", required=True )

    @api.constrains('fechainicio', 'fechatermino')
    def fechas_constrain(self):
        if self.fechainicio > self.fechatermino:
            raise ValidationError("La fecha de inicio no puede ser mayor a la de termino")
        elif self.fechatermino < self.fechainicio:
            raise ValidationError("La fecha de termino no puede ser menor a la de inicio")

    @api.one
    @api.depends('fechainicio', 'fechatermino')
    def calcular_dias(self):
        if self.fechainicio and self.fechatermino is False:
            self.plazodias = 0
        elif self.fechainicio and self.fechatermino:
            f1 = datetime.strptime(str(self.fechainicio), "%Y-%m-%d")
            f2 = datetime.strptime(str(self.fechatermino), "%Y-%m-%d")
            r = f2 - f1
            self.plazodias = r.days + 1

    plazodias = fields.Integer(string="Plazo/Días", compute="calcular_dias" )
    contratista = fields.Many2one('contratista.contratista', string='Contratista', required=True)
    # RECURSOS
    recurso_federal = fields.Float(string="Federal")
    recurso_federal_indirecto = fields.Float(string="Federal Indirecto")
    recurso_estatal = fields.Float(string="Estatal")
    recurso_estatal_indirecto = fields.Float(string="Estatal Indirecto")
    recurso_municipal = fields.Float(string="Municipal")
    recurso_municipal_indirecto = fields.Float(string="Municipal Indirecto")
    recurso_otros = fields.Float(string="Otros")
    total_recurso = fields.Float(string="Total", compute='sumaRecursos')

    estatus_adjudicacion = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_adjudicacion': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_adjudicacion': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_adjudicacion': 'validado'})

    @api.multi
    @api.onchange('programas_inversion_adjudicacion')
    def BorrarTabla(self):
        self.update({
            'programar_obra_adjudicacion': [[5]]
        })

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.iva = iva

    '''@api.one
    @api.depends('fechaadjudicacion')
    def VerificarContrato(self):
        contador = self.env['proceso.elaboracion_contrato'].search_count([('adjudicacion', '=', self.numerocontrato)])
        self.contratado = contador'''

    @api.multi
    @api.onchange('programar_obra_adjudicacion')
    def importe(self):
        suma = 0
        for i in self.programar_obra_adjudicacion:
            resultado = i.total_partida
            suma += resultado
            self.importe_adjudicacion = suma

    # METODO PARA INGRESAR A RECURSOS CON EL BOTON
    @api.multi
    def recursos(self):
        view = self.env.ref('proceso_contratacion.recursos_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'recursos',
            'res_model': 'proceso.adjudicacion_directa',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    # METODO PARA SUMA DE RECURSOS
    @api.one
    @api.depends('recurso_federal', 'recurso_federal_indirecto', 'recurso_estatal', 'recurso_estatal_indirecto',
                 'recurso_municipal', 'recurso_municipal_indirecto', 'recurso_otros')
    def sumaRecursos(self):
        for rec in self:
            rec.update({
                'total_recurso': (rec.recurso_federal + rec.recurso_federal_indirecto + rec.recurso_estatal +
                                  rec.recurso_estatal_indirecto + rec.recurso_municipal + rec.recurso_municipal_indirecto +
                                  rec.recurso_otros)
            })

