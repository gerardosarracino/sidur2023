# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo import exceptions


class Licitacion(models.Model):
    _name = "proceso.licitacion"
    _rec_name = 'numerolicitacion'
    #_inherit = ['mail.thread', 'mail.activity.mixin']

    # importacion
    id_sideop = fields.Integer()

    # verifica si esta contratada
    contratado = fields.Integer()
    # Verificar si fue fallada
    fallada = fields.Boolean()

    licitacion_id = fields.Char(compute="nombre", store=True)
    contratista = fields.Many2one('contratista.contratista', 'Contratista Ganador', compute="b_ganador")
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="programar_obra_licitacion.obra.obra_planeada.ejercicio")
    
    @api.one
    def b_ganador(self):
        b_ganador = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.id)])
        for i in b_ganador:
            if i.ganador is True:
                self.contratista = i.name
            else:
                print('No se encontró ganador')

    # PROGRAMA DE INVERSION
    programa_inversion_licitacion = fields.Many2one('generales.programas_inversion', 'Programa de Inversión', required=True)
    # OBRA / RECURSO A LICITAR
    programar_obra_licitacion = fields.Many2many("partidas.licitacion", string="Partida(s):", ondelete="restrict",)

    name = fields.Text(string="Objeto De La Licitación",)

    @api.multi
    @api.onchange('programar_obra_licitacion')
    def b_descripcion(self):
        s = ""
        for item in self.programar_obra_licitacion:
            s += item.obra.descripcion + "\n"
            self.name = s

    select = [('1', 'Licitación publica'), ('2', 'Licitación simplificada/Por invitación')]
    tipolicitacion = fields.Selection(select, string="Tipo de Licitación", required=True)

    numerolicitacion = fields.Char(string="Número de Licitación", required=True)

    estado_obra_desierta = fields.Integer(compute='estadoObraDesierta')
    estado_obra_cancelar = fields.Integer(compute='estadoObraCancelar')

    convocatoria = fields.Char(string="Convocatoria", )
    fechaconinv = fields.Date(string="Fecha Con/Inv", )
    select1 = [('1', 'Estatal'), ('2', 'Nacional'), ('3', 'Internacional')]
    caracter = fields.Selection(select1, string="Carácter", default="1", )
    select2 = [('1', 'Federal'), ('2', 'Estatal')]
    normatividad = fields.Selection(select2, string="Normatividad", required=True )

    # funcionariopresideactos = fields.Char(string="Funcionario que preside actos", )
    funcionariopresideactos = fields.Many2one(
        comodel_name='res.users',
        string='Funcionario que preside actos')

    puesto = fields.Text(string="Puesto", )
    numerooficio = fields.Char(string="Numero oficio", )
    fechaoficio = fields.Date(string="Fecha oficio", )
    oficioinvitacioncontraloria = fields.Char(string="Oficio invitación contraloría", )
    fechaoficio2 = fields.Date(string="Fecha oficio", )
    notariopublico = fields.Text(string="Notario publico", )
    fechalimiteentregabases = fields.Date(string="Fecha Límite para la entrega de Bases", )
    fecharegistrocompranet = fields.Date(string="Fecha Registro CompraNet", )
    costobasesdependencia = fields.Float(string="Costo de Bases Dependencia", )
    costocompranetbanco = fields.Float(string="Costo CompraNET/Banco",)
    fechaestimadainicio = fields.Date(string="Fecha Estimada de Inicio", required=True)
    fechaestimadatermino = fields.Date(string="Fecha Estimada de Termino", required=True)

    @api.multi
    def imprimir_documentos_licitacion(self):
        return {"type": "ir.actions.act_url", 
        "url": 'http://sidur.galartec.com/docx/LICITACION/id/' + str(self.id) , 
        "target": "new", }

    plazodias = fields.Integer(string="Plazo de Días", compute="calcular_dias", store=True)

    @api.one
    @api.depends('fechaestimadainicio', 'fechaestimadatermino')
    def calcular_dias(self):
        if self.fechaestimadainicio and self.fechaestimadatermino is False:
            self.plazodias = 0
        elif self.fechaestimadainicio and self.fechaestimadatermino:
            f1 = datetime.strptime(str(self.fechaestimadainicio), "%Y-%m-%d")
            f2 = datetime.strptime(str(self.fechaestimadatermino), "%Y-%m-%d")
            r = f2 - f1
            self.plazodias = r.days + 1

    capitalcontable = fields.Float(string="Capital Contable",)
    anticipomaterial = fields.Float(string="Anticipo Material %")
    anticipoinicio = fields.Float(string="Anticipo Inicio %")
    puntosminimospropuestatecnica = fields.Char(string="Puntos mínimos propuesta técnica")
    visitafechahora = fields.Datetime(string="Fecha/Hora")
    visitalugar = fields.Text(string="Lugar")
    juntafechahora = fields.Datetime(string="Fecha/Hora")
    juntalugar = fields.Text(string="Lugar")
    aperturafechahora = fields.Datetime(string="Fecha/Hora")
    aperturalugar = fields.Text(string="Lugar")
    fallofechahora = fields.Datetime(string="Fecha/Hora")
    fallolugar = fields.Text(string="Lugar")

    select3 = [('1', 'EN PROCESO, RECIEN CREADA'), ('2', 'EVENTO DE JUNTA DE ACLARACIONES'), ('3', 'APERTURA DE PROPUESTAS'),
               ('4', 'LICITACIÓN FALLADA CON GANADOR'), ('5', 'LICITACIÓN ENVIADA PARA SU CONTRATACIÓN'), ('998', 'DESIERTA') ,('999', 'CANCELADA')]

    estatus = fields.Selection(select3, string="Estatus de Licitación", default="1", compute="estatus_licitaciones")

   # ESTADO DE LA LICITACION
    @api.one
    def estatus_licitaciones(self):
        b_eventos = self.env['proceso.eventos_licitacion'].search([('numerolicitacion_evento.id', '=', self.id)])
        b_fallo = self.env['proceso.datos_fallo'].search([('numerolicitacion.id', '=', self.id)])
        if self.estado_obra_desierta >= 1:
            self.estatus = '998'
        elif self.estado_obra_cancelar >= 1:
            self.estatus = '999'
        else:
            estatus_aclaracion = ''
            estatus_propuesta = ''
            estatus_fallo = ''
            estatus_ganador = ''
            for i in b_eventos.contratista_aclaraciones:
                if i.asiste:
                    estatus_aclaracion = '2'
                else:
                    pass
            for x in b_eventos.contratista_propuesta:
                if x.revision:
                    estatus_propuesta = '3'
                else:
                    pass
            for y in b_eventos.contratista_fallo:
                if y.ganador:
                    estatus_fallo = '4'
                else:
                    pass
            for o in b_fallo:
                if o.ganador:
                    estatus_ganador = '5'
                else:
                    pass
            if estatus_aclaracion and not estatus_propuesta:
                self.estatus = estatus_aclaracion
            elif estatus_propuesta and not estatus_fallo:
                self.estatus = estatus_propuesta
            elif estatus_fallo and not estatus_ganador:
                self.estatus = estatus_fallo
            elif estatus_ganador:
                self.estatus = estatus_ganador
            else:
                pass


    variable_count = fields.Integer(compute='contar')

    estatus_licitacion = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    # METODO PARA INGRESAR A EVENTOS
    @api.multi
    def VentanaEventos(self): # SIDUR
        count = self.env['proceso.eventos_licitacion'].search_count([('numerolicitacion_evento.id', '=', self.id)])
        if count == 1:
            pass
        else:
            b_eve = self.env['proceso.eventos_licitacion']
            # CREAR EVENTO
            datos = {'numerolicitacion_evento': self.id}
            lista = b_eve.create(datos)

            # PRIMERA TABLA DE PARTICIPANTES
            b_participante = self.env['proceso.participante'].search(
                [('numerolicitacion.id', '=', self.id)])

            b_eve2 = self.env['proceso.eventos_licitacion'].browse(lista.id)
            for i in b_participante.contratista_participantes:
                # EVENTO DE VISITA
                datos2 = {
                    'contratista_participantes': [[0, 0, {'name': i.id, 'nombre_representante': i.nombre_representante,
                                                          'correo': i.correo}]]}
                x = b_eve2.write(datos2)
                # ACLARACIONES
                datos3 = {'contratista_aclaraciones': [
                        [0, 0, {'name': i.id, 'nombre_representante': i.nombre_representante,
                                'correo': i.correo, 'licitacion_id': self.id}]]}
                x3 = b_eve2.write(datos3)
                # PROPUESTAS
                datos4 = {'contratista_propuesta': [[0, 0,
                         {'name': i.id, 'nombre_representante': i.nombre_representante, 'numerolicitacion': self.id}]]}
                x4 = b_eve2.write(datos4)
                # PARTIDAS DE PROPUESTAS
                b_propuesta = self.env['proceso.contra_propuestas'].search([('numerolicitacion.id', '=', self.id),('name.id', '=', i.id)])
                for x in b_propuesta:
                    b_p = self.env['proceso.contra_propuestas'].browse(x.id)
                    if str(b_p.name.nombre_representante) == str(i.nombre_representante):
                        for u in self.programar_obra_licitacion:
                            datos_propuesta = {
                                'programar_obra_licitacion2': [[0, 0, {'recursos': u.recursos.id,
                                                                       'licitacion_id': self.id,
                                                                       'programaInversion': u.programaInversion.id
                                                                       }]]
                            }
                            p = b_p.write(datos_propuesta)
                    else:
                        pass

                # FALLO
                datos5 = {'contratista_fallo': [[0, 0, {'name': i.id, 'numerolicitacion': self.id}]]}
                x5 = b_eve2.write(datos5)

        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_eventos_form')
        # CONTADOR SI YA FUE CREADO

        # BUSCAR VISTA
        search = self.env['proceso.eventos_licitacion'].search([('numerolicitacion_evento.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if str(self.programar_obra_licitacion) == 'partidas.licitacion()':
            raise exceptions.Warning('Inserte una obra para poder proseguir!!')
        else:

            return {
                'type': 'ir.actions.act_window',
                'name': 'Eventos',
                'res_model': 'proceso.eventos_licitacion',
                'view_mode': 'form',
                'target': 'self',
                'view_id': view.id,
                'res_id': search.id,
            }


    # METODO PARA INGRESAR A PARTICIPANTES
    @api.multi
    def VentanaParticipantes(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_participantes_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.participante'].search_count([('numerolicitacion.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.participante'].search([('numerolicitacion.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if str(self.programar_obra_licitacion) == 'partidas.licitacion()':
            raise exceptions.Warning('Inserte una obra para poder proseguir!!')
        else:
            if count == 1:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Participantes',
                    'res_model': 'proceso.participante',
                    'view_mode': 'form',
                    'target': 'new',
                    'view_id': view.id,
                    'res_id': search.id,
                }
            # NO A SIDO CREADA LA VISTA, CREARLA
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Participantes',
                    'res_model': 'proceso.participante',
                    'view_mode': 'form',
                    'target': 'new',
                    'view_id': view.id,
                }

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_licitacion': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_licitacion': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_licitacion': 'validado'})

    @api.multi
    @api.onchange('programas_inversion_adjudicacion')
    def BorrarTabla(self):
        self.update({
            'programar_obra_adjudicacion': [[5]]
        })

    # METODO CONTADOR DE PARTICIPANTES
    @api.one
    def contar(self):
        b = self.env['proceso.participante'].search([('numerolicitacion', '=', self.id)])
        cont = 0
        for i in b.contratista_participantes:
            cont += 1
        self.variable_count = cont

    # METODO DE OBRA DESIERTA
    @api.one
    def estadoObraDesierta(self):
        resultado = self.env['proceso.estado_obra_desierta'].search_count([('numerolicitacion', '=', self.id)])
        self.estado_obra_desierta = resultado

    # METODO DE OBRA CANCELADA
    @api.one
    def estadoObraCancelar(self):
        resultado = self.env['proceso.estado_obra_cancelar'].search_count([('numerolicitacion', '=', self.id)])
        self.estado_obra_cancelar = resultado

    # ENLACE CON LA LICITACION
    @api.one
    def nombre(self):
        self.licitacion_id = self.numerolicitacion

    @api.multi
    def licitacion_cancelar(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.estado_obra_cancelado_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.estado_obra_cancelar'].search_count([('numerolicitacion.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.estado_obra_cancelar'].search([('numerolicitacion.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cancelar Licitacion',
                'res_model': 'proceso.estado_obra_cancelar',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cancelar Licitacion',
                'res_model': 'proceso.estado_obra_cancelar',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_numerolicitacion': self.id},
                'view_id': view.id,
            }

    @api.multi
    def licitacion_desierta(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.estado_obra_desierta_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.estado_obra_desierta'].search_count([('numerolicitacion.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.estado_obra_desierta'].search([('numerolicitacion.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Desierta',
                'res_model': 'proceso.estado_obra_desierta',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Desierta',
                'res_model': 'proceso.estado_obra_desierta',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_numerolicitacion': self.id},
                'view_id': view.id,
            }

# EVENTOS DE LICITACION
class Eventos(models.Model):
    _name = 'proceso.eventos_licitacion'
    _rec_name = 'numerolicitacion_evento'

    id_sideop = fields.Integer()
    licitacion_id = fields.Char(compute="nombre", store=True, ondelete="cascade")

    numerolicitacion_evento = fields.Many2one('proceso.licitacion', string='Numero Licitación:', readonly=True,
                                              store=True, ondelete="cascade")

    contratista_participantes = fields.Many2many('proceso.contra_participantev', store=True, ondelete="restrict")
    contratista_aclaraciones = fields.Many2many('proceso.contra_aclaraciones', store=True, ondelete="restrict")
    contratista_propuesta = fields.Many2many('proceso.contra_propuestas', store=True, ondelete="resctrict")
    contratista_fallo = fields.Many2many('proceso.contra_fallo', store=True, ondelete="restrict")

    # AUXILIAR PARA ACCIONAR METODO
    aux = fields.Float(string="aux",  required=False, )

    # METODO PARA INGRESAR A DATOS GENERALES DEL FALLO
    @api.multi
    def dato_fallo(self):
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.datos_fallo'].search_count([('id_eventos.id', '=', self.id)])
        if count == 1:
            pass
        else:
            b_eve = self.env['proceso.datos_fallo']
            # CREAR EVENTO
            datos = {'id_eventos': self.id, 'numerolicitacion': self.numerolicitacion_evento.id}
            lista = b_eve.create(datos)

        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_fallo_datos_form')
        # BUSCAR VISTA
        search = self.env['proceso.datos_fallo'].search([('id_eventos.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fallo',
            'res_model': 'proceso.datos_fallo',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': search.id,
        }


    @api.one
    def nombre(self):
        self.licitacion_id = self.id

    # METODO ACTUALIZAR TABLAS DE EVENTOS
    @api.multi
    def llenar_evento(self):
        b_participante = self.env['proceso.participante'].search(
            [('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
        acum = 0
        re = ''
        for x in b_participante.contratista_participantes:
            print(x.name)
            acum += 1
            b_visita = self.env['proceso.contra_participantev'].search_count(
                [('name.id', '=', x.id), ('licitacion_id.id', '=', self.numerolicitacion_evento.id)])
            b_aclaracion = self.env['proceso.contra_aclaraciones'].search_count(
                [('name.id', '=', x.id), ('licitacion_id.id', '=', self.numerolicitacion_evento.id)])
            b_propuesta = self.env['proceso.contra_propuestas'].search_count(
                [('name.id', '=', x.id), ('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
            b_fallo = self.env['proceso.contra_fallo'].search_count(
                [('name.id', '=', x.id), ('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
            print('sdada', b_fallo)
            if b_visita == 0:
                print('xdd')
                self.update({
                    'contratista_participantes': [[0, 0, {'name': x.id, 'nombre_representante': x.nombre_representante,
                                                          'correo': x.correo,
                                                          'licitacion_id': self.numerolicitacion_evento.id}]]
                })
            if b_aclaracion == 0:
                # ACLARACIONES
                self.update({'contratista_aclaraciones': [
                    [0, 0, {'name': x.id, 'nombre_representante': x.nombre_representante,
                            'correo': x.correo, 'licitacion_id': self.numerolicitacion_evento.id}]]})

            if b_fallo == 0:
                print('SI ENTROOOOOOOOOOOOOOOOOOOOOOOOOOO')
                self.update({'contratista_fallo': [[0, 0, {'name': x.id,
                                                           'numerolicitacion': self.numerolicitacion_evento.id}]]})

            if b_propuesta == 0:
                # PROPUESTAS
                self.update({'contratista_propuesta': [[0, 0,
                                                        {'name': x.id, 'nombre_representante': x.nombre_representante,
                                                         'numerolicitacion': self.numerolicitacion_evento.id}]]})

                b_propuesta_s = self.env['proceso.contra_propuestas'].search(
                    [('name.id', '=', x.id), ('numerolicitacion.id', '=', self.numerolicitacion_evento.id)])
                for g in b_propuesta_s:
                    pp = self.env['proceso.contra_propuestas'].browse(g.id)
                    for u in self.numerolicitacion_evento.programar_obra_licitacion:

                        print(pp,'xxxxxxxxxxxxxxxxx')
                        datos_propuesta = {
                            'programar_obra_licitacion2': [[0, 0, {'recursos': u.recursos.id,
                                                                   'licitacion_id': self.numerolicitacion_evento.id,
                                                                   'programaInversion': u.programaInversion.id
                                                                   }]]
                        }
                        pp.write(datos_propuesta)

        lista = []
        for contratista in b_participante.contratista_participantes:
            lista.append(str(contratista.id))

        for v in self.contratista_participantes:
            if not str(v.name.id) in lista:
                print('no :c', v.name.name)
                un = v.unlink()
        for v in self.contratista_aclaraciones:
            if not str(v.name.id) in lista:
                print('no :c', v.name.name)
                un = v.unlink()
        for v in self.contratista_propuesta:
            if not str(v.name.id) in lista:
                tb = v.programar_obra_licitacion2.unlink()
                print('no :c', v.name.name)
                un = v.unlink()
        for v in self.contratista_fallo:
            if not str(v.name.id) in lista:
                print('no :c', v.name.name)
                un = v.unlink()

    programar_obra_licitacion2 = fields.Many2many("proceso.propuesta_lic", string="Partida(s):", store=True)


# VISITA DE OBRA
class ContratistaParticipanteV(models.Model):
    _name = 'proceso.contra_participantev'

    id_sideop = fields.Integer()
    licitacion_id = fields.Many2one('proceso.licitacion', readonly=True)
    name = fields.Many2one('contratista.contratista', 'Contratista')
    # name = fields.Char(string="Licitante:")
    nombre_representante = fields.Char(string="Nombre del Representante:")
    correo = fields.Char(string="Correo:")
    asiste = fields.Boolean('Asiste')

    @api.multi
    def borrar(self):
        self.env['proceso.contra_participantev'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


# JUNTA ACLARACIONES
class JuntaAclaraciones(models.Model):
    _name = 'proceso.contra_aclaraciones'

    id_sideop = fields.Integer()
    licitacion_id = fields.Many2one('proceso.licitacion', readonly=True)
    # name = fields.Char(string="Licitante:")
    name = fields.Many2one('contratista.contratista', 'Contratista')
    nombre_representante = fields.Char(string="Nombre del Representante:")
    correo = fields.Char(string="Correo:")
    asiste = fields.Boolean('Asiste')

    preguntas = fields.Many2many("proceso.preguntas", string="Preguntas del Licitante")

    @api.multi
    def borrar(self):
        self.env['proceso.contra_aclaraciones'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # METODO PARA INGRESAR A ACLARACIONES
    @api.multi
    def aclaraciones(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_aclaraciones_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_aclaraciones'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_aclaraciones'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Preguntas',
                'res_model': 'proceso.contra_aclaraciones',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Preguntas',
                'res_model': 'proceso.contra_aclaraciones',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }


# CLASE DE PREGUNTAS DE ACLARACIONES
class Preguntas(models.Model):
    _name = 'proceso.preguntas'

    pregunta = fields.Char(string="Pregunta:", required=False, )
    respuesta = fields.Text(string="Respuesta:", required=False, )


# Apertura de Propuestas
class AperturaPropuestas(models.Model):
    _name = 'proceso.contra_propuestas'

    id_sideop = fields.Integer()
    id_eventos = fields.Many2one('proceso.eventos_licitacion', string='id evento:', required=True, compute='b_evento')

    @api.one
    def b_evento(self):
        b_eve = self.env['proceso.eventos_licitacion'].search(
            [('numerolicitacion_evento.id', '=', self.numerolicitacion.id)])
        self.id_eventos = b_eve.id

    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:')

    # name = fields.Char(string="Licitante:", )
    name = fields.Many2one('contratista.contratista', 'Contratista')

    monto = fields.Float(string="Monto:", readonly=True)
    asiste = fields.Boolean('Asiste')
    completa = fields.Boolean('Completa')
    revision = fields.Boolean('Para revisión')
    puntos_tecnicos = fields.Float('Puntos Tecnicos')
    puntos_economicos = fields.Float('Puntos Economicos')
    paso = fields.Boolean('Pasó')

    posicion = fields.Selection([('1', 'Posición #1')], 'Posición')

    programar_obra_licitacion2 = fields.Many2many("proceso.propuesta_lic", string="Partida(s):", ondelete="cascade") #

    aux = fields.Float(string="aux", required=False, )

    observaciones = fields.Text(string="Observaciones:", required=False, )

    @api.multi
    def borrar(self):
        self.env['proceso.contra_propuestas'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # AUXILIAR PARA ACCIONAR METODO

    # SUMA DE LOS MONTOS
    @api.multi
    @api.onchange('programar_obra_licitacion2')
    def sumMonto(self):
        sum = 0
        for i in self.programar_obra_licitacion2:
            sum = sum + i.monto_partida
            self.monto = sum

    # METODO PARA INGRESAR A PROPUESTAS BOTON
    @api.multi
    def propuestas(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_propuesta_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_propuestas'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_propuestas'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Propuesta',
                'res_model': 'proceso.contra_propuestas',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Propuesta',
                'res_model': 'proceso.contra_propuestas',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }


# FALLO DE LICITACIONES
class Fallo(models.Model):
    _name = 'proceso.contra_fallo'

    id_sideop = fields.Integer()
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:')
    id_eventos = fields.Many2one('proceso.eventos_licitacion', string='id evento:')

    # name = fields.Char(string="Licitante:")
    name = fields.Many2one('contratista.contratista', 'Contratista')
    monto = fields.Float(string="Monto Fallado A/I.V.A:", compute="b_monto")
    posicion = fields.Selection([('1', 'Posición #1')], 'Posición', compute="b_monto")
    nombre_representante = fields.Char(string="Nombre del Representante:")

    @api.multi
    def borrar(self):
        self.env['proceso.contra_fallo'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # METODO PARA TRAER LOS DATOS DEL MONTO Y POSICION DE LA PROPUESTA
    @api.one
    def b_monto(self):
        b_mont = self.env['proceso.contra_propuestas'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        acum = 0
        for i in b_mont:
            if int(i.name.id) == int(self.name.id):
                if i.posicion:
                    for x in i.programar_obra_licitacion2:
                        acum += x.monto_partida
                    self.monto = acum
                    self.posicion = i.posicion
                else:
                    pass
            else:
                pass

    asiste = fields.Boolean('Asistió')
    ganador = fields.Boolean('Ganador')
    puntos_tecnicos = fields.Float('Puntos Tecnicos')
    puntos_economicos = fields.Float('Puntos Economicos')

    observaciones = fields.Text(string="Observaciones")

    contador_ganador = fields.Integer(compute="ganador_count")

    # METODO PARA VERIFICAR SI YA HAY GANADOR, PARA ATRIBUTO READONLY EN LA VISTA
    @api.one
    def ganador_count(self):
        b_fallo = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        for i in b_fallo:
            print(i.ganador)
            if i.ganador is True:
                self.contador_ganador = 1

    # METODO PARA INGRESAR A FALLO BOTON
    @api.multi
    def fallo(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_fallo_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['proceso.contra_fallo'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['proceso.contra_fallo'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.contra_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Fallo',
                'res_model': 'proceso.contra_fallo',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }
    
    @api.onchange('ganador')
    def licitada(self):
        if self.ganador:
            for i in self.numerolicitacion.programar_obra_licitacion:
                b_obra = self.env['registro.programarobra'].browse(i.obra.id)
                b_lic = self.env['proceso.licitacion'].browse(self.numerolicitacion.id)
                datos = {'obra_adj_lic': True}
                datos2 = {'fallada': True}
                lista = b_obra.write(datos)
                lista2 = b_lic.write(datos2)
        else:
            pass


# VENTANA DE DATOS DEL FALLO
class DatosFallo(models.Model):
    _name = 'proceso.datos_fallo'
    _rec_name = 'ganador'

    id_sideop = fields.Integer()
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:', readonly=True, store=True)
    id_eventos = fields.Many2one('proceso.eventos_licitacion', string='id evento:', readonly=True, store=True)

    # ganador = fields.Char(string="Ganador:", compute="b_ganador")
    ganador = fields.Many2one('contratista.contratista', 'Contratista', compute="b_ganador")

    @api.one
    def b_ganador(self):
        b_ganador = self.env['proceso.contra_fallo'].search([('numerolicitacion.id', '=', self.numerolicitacion.id)])
        for i in self.id_eventos.contratista_fallo:
            if i.ganador is True:
                self.importe_ganador = i.monto
                self.ganador = i.name.id
            else:
                print('No se encontró ganador')

    fecha_fallo = fields.Date(string="Fecha Fallo:")
    hora_inicio_f = fields.Datetime(string="Hora de Inicio Fallo:")
    hora_termino_f = fields.Datetime('Hora Termino Fallo:')

    hora_inicio_o = fields.Date('Fecha Inicio Obra:', related="numerolicitacion.fechaestimadainicio")

    hora_termino_o = fields.Date('Fecha Termino Obra:', related="numerolicitacion.fechaestimadatermino")

    plazo = fields.Integer('Plazo', related="numerolicitacion.plazodias")
    hora_antes_firma = fields.Datetime('Hora Antes Firma Contrato:')
    fecha_fcontrato = fields.Date('Fecha firma contrato:')

    importe_ganador = fields.Float('Importe Ganador:', compute="b_ganador")
    iva = fields.Float('I.V.A', default=0.16)

    # CALCULO DEL IVA
    @api.one
    def fallo_iva(self):
        self.total_contratado = (self.iva * self.importe_ganador) + self.importe_ganador

    total_contratado = fields.Float('Total Contratado:	', compute="fallo_iva")

    # RELACION PARA EL DOMAIN DEL ANEXO TECNICO DEL RECURSO DE LA LICITACION
    relacion_concepto_ofi = fields.Text(related="numerolicitacion.programar_obra_licitacion.recursos.concepto.descripcion") #
    # SELECCION DEL RECURSO PARA LA LICITACION
    recursos = fields.Many2many('autorizacion_obra.anexo_tecnico', string="Seleccione un oficio de autorización",
                                compute="recursos_fallo")
    @api.one
    def recursos_fallo(self):
        fallo = self.env['proceso.datos_fallo']
        b_lic = self.env['proceso.licitacion'].search([('id', '=', self.numerolicitacion.id)])
        acum = 0
        for i in b_lic.programar_obra_licitacion:
            datos_recursos = {
                'recursos': [[4, i.recursos.id, {
                }]]}
            r = fallo.browse(self.id)
            recurso = r.update(datos_recursos)


# TABLA DE PROPUESTA DEL LICITANTE
class PropuestaLic(models.Model):
    _name = 'proceso.propuesta_lic'

    id_sideop = fields.Integer()
    licitacion_id = fields.Many2one('proceso.licitacion')
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')

    obra = fields.Many2one('registro.programarobra', related="recursos.concepto")
    programaInversion = fields.Many2one('generales.programas_inversion')

    monto_partida = fields.Float(string="" )
    
    @api.multi
    def borrar(self):
        self.env['proceso.propuesta_lic'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

class Participante(models.Model):
    _name = 'proceso.participante'

    id_sideop = fields.Char()
    licitacion_id = fields.Char(compute="nombre", store=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    contratista_participantes = fields.Many2many('contratista.contratista')

    @api.multi
    def ver_contratistas(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contratistas',
            'res_model': 'contratista.contratista',
            'view_mode': 'tree,form',
        }
    
    @api.one
    def nombre(self):
        self.licitacion_id = self.id


class EstadoObraDesierta(models.Model):
    _name = 'proceso.estado_obra_desierta'
    _rec_name = 'estado_obra_desierta'

    obra_id_desierta = fields.Char(compute="estadoObra", store=True)
    licitacion_id = fields.Char(compute="nombre", store=True)
    estado_obra_desierta = fields.Char(string="estado obra", default="Desierta", readonly=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    fecha_desierta = fields.Date(string="Fecha de Desierta:")
    observaciones_desierta = fields.Text(string="Observaciones:")

    @api.one
    def estadoObra(self):
        self.obra_id_desierta = self.estado_obra_desierta

    @api.one
    def nombre(self):
        self.licitacion_id = self.id


class EstadoObraCancelar(models.Model):
    _name = 'proceso.estado_obra_cancelar'

    obra_id_cancelar = fields.Char(compute="estadoObra", store=True)
    licitacion_id = fields.Char(compute="nombre", store=True)
    estado_obra_cancelar = fields.Char(string="estado obra", default="Cancelada", readonly=True)
    numerolicitacion = fields.Many2one('proceso.licitacion', string='Numero Licitación:',
                                       readonly=True)
    fecha_cancelado = fields.Date(string="Fecha de Cancelacion:")
    observaciones_cancelado = fields.Text(string="Observaciones:")

    @api.one
    def estadoObraCancelar(self):
        self.obra_id_cancelar = self.estado_obra_cancelar

    @api.one
    def nombre(self):
        self.licitacion_id = self.id



