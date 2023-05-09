# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

from odoo import models, fields, api
from datetime import datetime


class TipoAuditoria(models.Model):
    _name = 'auditorias.tipo_auditoria'
    _rec_name = 'tipo_auditoria'
    tipo_auditoria = fields.Char(string='Tipo de auditoria')


class NumeroAuditoria(models.Model):
    _name = 'auditorias.num_auditoria'
    _rec_name = 'numero_auditoria'
    numero_auditoria = fields.Char(string='Número de auditoria')


class OficioCierre(models.Model):
    _name = 'auditorias.cierre'
    _rec_name = 'oficio_cierre'
    oficio_cierre = fields.Char(string='Oficio de cierre')


class Responsable(models.Model):
    _name = 'auditorias.responsable'
    responsable = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user.id,
        required=True
    )
    funcion = fields.Char(string='Función', required=True)


class OficioNotificacion(models.Model):
    _name = 'auditorias.oficio_noti'
    _rec_name = 'num_oficio_noti'
    num_oficio_noti = fields.Char(string='Oficio de notificación', required=True)
    desc_inf_solic = fields.Text(string='Descripción de la información solicitada', required=True)
    tipo_auditoria = fields.Many2one('auditorias.tipo_auditoria', string='Tipo de auditoria', required=True)
    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_vencimiento = fields.Date(string='Fecha de vencimiento', required=True)
    numero_auditoria = fields.Many2one('auditorias.num_auditoria', string='Número de auditoria', required=True)
    subir_oficio = fields.Binary(string='Subir oficio')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))


class RespuestaNotificacion(models.Model):
    _name = 'auditorias.resp_noti'
    name = fields.Char()
    respuesta_notif = fields.Char(string='Respuesta de notificación', required=True)
    oficio_notificacion = fields.Many2one('auditorias.oficio_noti', string='Oficio de notificación', required=True)
    resp_info_solic = fields.Text(string='Respuesta de la información solicitada', required=True)
    responsable = fields.Many2many('auditorias.responsable', string='Responsable')
    fecha = fields.Date(string='Fecha', required=True)
    subir_oficio = fields.Binary(string='Subir oficio')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))


class ActaInicioAuditoria(models.Model):
    _name = 'auditorias.acta_inicio'
    numero_auditoria = fields.Char(string='Número de auditoria', required=True)
    oficio_inicio = fields.Char(string='Oficio de inicio', required=True)
    oficio_notificacion = fields.Many2one('auditorias.oficio_noti', string='Oficio de notificación', required=True)
    fecha = fields.Date(string='Fecha', required=True)
    subir_oficio = fields.Binary(string='Subir oficio')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))


class OficioPrecierre(models.Model):
    _name = 'auditorias.oficio_precierre'
    oficio_precierre = fields.Char(string='Oficio de precierre', required=True)
    numero_auditoria = fields.Many2one('auditorias.num_auditoria', string='Número de auditoria', required=True)
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))


class Observacion(models.Model):
    _name = 'auditorias.observacion'
    numero = fields.Char(string='Número', required=True)
    contrato = fields.Many2one('proceso.elaboracion_contrato', required=True)
    contratista = fields.Char(related='contrato.contratista.name', string='Contratista')

    residente = fields.Many2one('res.users', store=True, string='Supervisor')
    descripcion = fields.Html(string='Descripción')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))

    @api.multi
    @api.onchange('contrato')
    def supervisor(self):
        if not self.contrato:
            pass
        else:
            partida = self.env['partidas.partidas'].search([('nombre_contrato', '=', self.contrato.contrato)])
            print("Esto trae partida", self.contrato.id ,partida.residente_obra, partida.nombre_contrato)
            for p in partida.residente_obra:
                print("esto trae el for", p)
                self.residente = p.id


class Respuestas(models.Model):
    _name = 'auditorias.respuestas'
    name = fields.Char()
    observacion = fields.Integer(string='Observación', required=True)
    oficio = fields.Many2one('auditorias.oficio_noti', string='Oficio', required=True)
    oficio_precierre = fields.Many2one('auditorias.oficio_precierre', string='Oficio de precierre', required=True)
    oficio_ciere = fields.Many2one('auditorias.cierre', string='Oficio de cierre', required=True)
    medida_solventacion = fields.Text(string='Medida de solventación', required=True)
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))


class OficioCierre_(models.Model):
    _name = 'auditorias.oficio_cierre'
    oficio_cierre = fields.Char(string='Oficio de cierre', required=True)
    no_oficio_noti = fields.Many2one('auditorias.oficio_noti', string='Oficio de notificación', required=True)
    observaciones = fields.Many2many('auditorias.observacion', required=True)
    solventada = fields.Selection([('si', 'SI'), ('no', 'NO'), ('parcialmente solventada', 'Parcialmente Solventada'), ], string='Solventada', required=True, default='si')
    capturista = fields.Char("Capturista", default=lambda self: self.env.user.name)
    fecha_captura = fields.Date(string='Fecha de captura', default=lambda s: fields.Date.context_today(s))