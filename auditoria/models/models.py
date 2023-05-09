# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TipoAuditoria(models.Model):
    _name = 'auditoria.tipo_auditoria'
    _rec_name = 'tipo_auditoria'
    tipo_auditoria = fields.Char()


class TipoActa(models.Model):
    _name = 'auditoria.tipo_acta'
    _rec_name = 'tipo_acta'
    tipo_acta = fields.Char(string='Tipo de documento')


class Responsable(models.Model):
    _name = 'auditoria.responsable'
    _rec_name = 'responsable'
    responsable = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user.id,
        required=True
    )
    funcion = fields.Char(string='Función', required=True)


class Estatus(models.Model):
    _name = 'auditoria.estatus'
    _rec_name = 'estatus'
    estatus = fields.Char(string='Estatus')


class Funcion(models.Model):
    _name = 'auditoria.funcion'
    _rec_name = 'nombre'
    nombre = fields.Char(string='Nombre')


class Auditoria(models.Model):
    _name = 'auditoria.auditoria'
    _rec_name = 'numero_auditoria'
    numero_auditoria = fields.Char(string='Número de auditoría', required=True)
    tipo_auditoria = fields.Many2one('auditoria.tipo_auditoria', string='Tipo de auditoría', required=True)
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))
    fecha_inicio = fields.Date(string='Fecha de inicio', readonly=True, compute='fechas_seguimiento')
    fecha_termino = fields.Date(string='Fecha de término', readonly=True, compute='fechas_seguimiento')
    contar_observaciones = fields.Integer(compute='observaciones')
    contar_seguimientos = fields.Integer(compute='seguimiento')

    @api.one
    def fechas_seguimiento(self):
        seguimiento = self.env['auditoria.seguimiento'].search([('auditoria','=',self.id)])
        for s in seguimiento:
            tipo_documento = s.tipo_acta.tipo_acta
            if tipo_documento == str('Oficio de notificación'):
                self.fecha_inicio = s.fecha_inicio
                self.fecha_termino = s.fecha_cierre

    @api.one
    def observaciones(self):
        count = self.env['auditoria.observacion'].search_count([('auditoria', '=', self.id)])
        self.contar_observaciones = count

    @api.one
    def seguimiento(self):
        count = self.env['auditoria.seguimiento'].search_count([('auditoria', '=', self.id)])
        self.contar_seguimientos = count


class Seguimiento(models.Model):
    _name = 'auditoria.seguimiento'
    _rec_name = 'numero_documento'
    auditoria = fields.Many2one('auditoria.auditoria', string='Auditoría', required=True)
    tipo_acta = fields.Many2one('auditoria.tipo_acta', required=True)
    numero_documento = fields.Char(string='Número de documento')
    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_cierre = fields.Date(string='Fecha de cierre', required=True)
    descripcion = fields.Html(string='Descripción')
    documento = fields.Binary(string='Subir documento')
    responsable = fields.Many2many('auditoria.responsable', required=True)
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))
    obs = fields.Integer(compute='contar_observaciones')

    @api.one
    def contar_observaciones(self):
        count = self.env['auditoria.observacion'].search_count([('seguimiento','=',self.id)])
        self.obs = count


class Observacion(models.Model):
    _name = 'auditoria.observacion'
    _rec_name = 'numero'
    numero = fields.Char(string='Número', required=True)
    auditoria = fields.Many2one('auditoria.auditoria', required=True)
    contrato = fields.Many2one('proceso.elaboracion_contrato', required=True)
    descripcion = fields.Html(string='Descripción')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))
    respuesta = fields.Integer(compute='contar_respuestas')
    estado_resp = fields.Char(compute='estado_respuesta')
    fecha_inicio = fields.Date(related='auditoria.fecha_inicio')
    fecha_termino = fields.Date(related='auditoria.fecha_termino')

    @api.one
    def estado_respuesta(self):
        resp = self.env['auditoria.resp_obs'].search([('observacion','=',self.id)])
        for r in resp:
            self.estado_resp = r.estatus.nombre

        if self.estado_resp:
            pass
        else:
            self.estado_resp = str("Sin respuesta")

    @api.one
    def contar_respuestas(self):
        count = self.env['auditoria.resp_obs'].search_count([('observacion','=',self.id)])
        self.respuesta = count


class RespuestaObservacion(models.Model):
    _name = 'auditoria.resp_obs'
    _rec_name = 'oficio_respuesta'
    oficio_respuesta = fields.Char(string='Número de oficio de respuesta', required=True)
    seguimiento = fields.Many2one('auditoria.seguimiento')
    observacion = fields.Many2one('auditoria.observacion')
    respuesta = fields.Html(string='Respuesta')
    oficio = fields.Selection([('precierre', 'Precierre'), ('cierre', 'Cierre')], string='Oficio',
                              required=True, default='precierre ')
    estatus = fields.Many2one('auditoria.funcion', required=True)
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))
