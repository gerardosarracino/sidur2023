# -*- coding: utf-8 -*-

from odoo import exceptions
from odoo import api, fields, models, _
import datetime


class ElaboracionContratos(models.Model):
    _name = "proceso.elaboracion_contrato"
    _rec_name = 'contrato'

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", store=True)

    # CONSULTA LIBROS BLANCOS
    localidad = fields.Text(string="Localidad", readonly="True")
    
    # IVA FRONTERA
    iva_frontera = fields.Boolean(string="Es iva de frontera?")

    @api.multi
    @api.onchange('iva_frontera')
    def actualizar_iva_frontera(self):
        if self.iva_frontera:
            iva = 0.08
        else:
            iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        if self.tipo_contrato == "1": # LIC
            for i in self.contrato_partida_licitacion:
                i.write({'iva_frontera': self.iva_frontera})
                i.write({'iva_partida': i.monto_partida * float(iva),
                         'total_partida': (i.monto_partida * float(iva)) + i.monto_partida,
                         'total': i.monto_partida,
                         'total_iva': i.monto_partida * float(iva),
                         'total_civa': (i.monto_partida * float(iva)) + i.monto_partida,
                         })
        else: # ADJ
            for i in self.contrato_partida_adjudicacion:
                i.write({'iva_frontera': self.iva_frontera})
                i.write({'iva_partida': i.monto_partida * float(iva),
                         'total_partida': (i.monto_partida * float(iva)) + i.monto_partida,
                         'total': i.monto_partida,
                         'total_iva': i.monto_partida * float(iva),
                         'total_civa': (i.monto_partida * float(iva)) + i.monto_partida,
                         })

    estado_obra_m2o = fields.Many2one('semaforo.estado_obra_lista', string="Estado", store=True) 

    @api.multi
    @api.onchange('fecha', 'contrato', 'fechainicio')
    def b_ejer(self):
        year = datetime.date.today().year
        b_eje = self.env['registro.ejercicio'].search([])
        for i in b_eje:
            if str(year) == str(i.name):
                self.ejercicio = i.id
            else:
                pass
            
    # contador para esconder los pages
    contrato_contador = fields.Integer(compute="contar_contrato")

    @api.one
    def contar_contrato(self):
        b_contrato = self.env['proceso.elaboracion_contrato'].search_count([('id', '=', self.id)])
        self.contrato_contador = b_contrato

    # IMPORTACION
    id_contratista = fields.Char('id contratista')
    id_residente = fields.Char('id _residente')
    num_contrato_sideop = fields.Char('numero contrato sideop')
    id_sideop_partida = fields.Integer('ID SIDEOP part')

    radio_adj_lic = [('1', "Licitación"), ('2', "Adjudicación")]
    tipo_contrato = fields.Selection(radio_adj_lic, string="Tipo de Contrato:", store=True, required=True)

    contrato_partida_licitacion = fields.Many2many('partidas.partidas', ondelete="restrict")

    contrato_partida_adjudicacion = fields.Many2many('partidas.partidas', ondelete="restrict")

    # LICITACION PARTIDAS
    obra = fields.Many2one('proceso.licitacion', string="Seleccionar obra", domain="['&', ('contratado', '=', 0), ('fallada', '=', True)]")
    # ADJUDICACION PARTIDAS
    adjudicacion = fields.Many2one('proceso.adjudicacion_directa', string="Nombre de Adjudicación")

    # CONTAR REGISTROS DE FINIQUITO
    contar_finiquito = fields.Integer(compute='contar', string="PRUEBA")
    # CONTAR REGISTROS DE CONVENIO
    contar_convenio = fields.Integer(compute='contar2', string="PRUEBA")
    fecha = fields.Date(string="Fecha",  default=fields.Date.today(), required=True)

    contrato = fields.Char(string="Contrato", related="adjudicacion.numerocontrato", readonly=False, store=True, required=True)

    name = fields.Text(string="Descripción/Meta")

    @api.onchange('obra', 'adjudicacion')
    def b_descripcion(self):
        if self.tipo_contrato == '2':
            self.name = self.adjudicacion.name
        elif self.tipo_contrato == '1':
            self.name = self.obra.name

    descripciontrabajos = fields.Text(string="Descripción trabajos:", )
    unidadresponsableejecucion = fields.Many2one('proceso.unidad_responsable', string="Unidad responsable de su "
                                                                                      "ejecución", required=True)
    supervisionexterna = fields.Text(string="Supervisión externa")
    supervisionexterna1 = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:")

    contratista = fields.Many2one('contratista.contratista', )

    @api.onchange('obra', 'adjudicacion')
    def b_contratista(self):
        if self.tipo_contrato == '2':
            self.contratista = self.adjudicacion.contratista
        elif self.tipo_contrato == '1':
            self.contratista = self.obra.contratista

    fechainicio = fields.Date(string="Fecha de Inicio", required=True)
    fechatermino = fields.Date(string="Fecha de Termino", required=True)

    @api.onchange('obra', 'adjudicacion')
    def b_fechas(self):
        if self.tipo_contrato == '2':
            self.fechainicio = str(self.adjudicacion.fechainicio)
            self.fechatermino = str(self.adjudicacion.fechatermino)
        elif self.tipo_contrato == '1':
            self.fechainicio = str(self.obra.fechaestimadainicio)
            self.fechatermino = str(self.obra.fechaestimadatermino)

    periodicidadretencion = fields.Selection([('DIARIO', 'DIARIO'),('MENSUAL','MENSUAL'),('ninguno','Ninguno')],
                                             string="Periodicidad Retención",  default='ninguno')
    retencion = fields.Float(string="% Retención")
    sancion = fields.Float(string="% Sanción", digits=(12,3))
    # Fianzas
    fianzas = fields.Many2many('proceso.fianza', string="Fianzas:")
    # Deducciones
    deducciones = fields.Many2many("generales.deducciones", string="Deducciones")
    # RECURSOS ANEXOS
    anexos = fields.Many2many('autorizacion_obra.anexo_tecnico', 'nombre_lista', string="Anexos:", compute="llenar_anexo")

    enlace_oficio = fields.Many2one('autorizacion_obra.oficios_de_autorizacion', string="Enlace a Oficio", compute='calculo_recursos', store=True)

    recurso_autorizado = fields.Float(string='Recursos Autorizados:', compute='calculo_recursos')

    @api.multi
    def calculo_recursos(self):
        acum = 0
        acumx = 0
        for i in self.anexos:
            acum += i.total1
            acumx += i.total_ca
            self.recurso_autorizado = acum
            self.importe_cancelado = acumx

    importe_cancelado = fields.Float(string='Recursos Cancelados:', compute='calculo_recursos')

    total_recurso_aut = fields.Float(string='Total de Recursos Autorizados:', compute="recurso_total")

    # TOTAL DEL CONTRAO Y NUEVO CAMPO TOTAL PARA CONVENIO
    convenios_escalatorias = fields.Float(string="Convenios y Escalatorias:", readonly="True")

    total_contratado = fields.Float(string="Total Contratado:", compute="contratado_total")
    total_contratado_modificado = fields.Float(string="Total Contratado:", compute="contratado_total_modi")

    saldo = fields.Float(string="Saldo:", compute="saldo_total")

    # RELATED CON LA OBRA DE LA PARTIDA PARA RELACIONARLA CON EL ANEXO TECNICO
    obra_partida = fields.Many2one(string="obra partida adjudicacion", related="contrato_partida_adjudicacion.obra")
    obra_partida_licitacion = fields.Many2one(string="obra partida licitacion", related="contrato_partida_licitacion.recursos")

    # IMPORTE DEL CONTRATO LICITACION Y ADJUDICACION
    impcontra = fields.Float(string="Importe:", compute="importeT", store=True)
    impcontra_iva = fields.Float(string="Importe:", compute="importeT", store=True)
    total_civa = fields.Float(string="Monto Total Contratado cIva:", digits=(12,2), store=True)

    estatus_contrato = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_contrato': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_contrato': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_contrato': 'validado'})

    # METODO PARA MANDAR PARAMETRO QUE IDENTIFICAR QUE ADJUDICACION Y LICITACION FUE CONTRATADA YA
    @api.model
    def create(self, values):
        if values['tipo_contrato'] == '2':
            b_adj = self.env['proceso.adjudicacion_directa'].browse(values['adjudicacion'])
            b_adj.write({'contratado': 1})
        elif values['tipo_contrato'] == '1':
            b_lici = self.env['proceso.licitacion'].browse(values['obra'])
            b_lici.write({'contratado': 1})

        var = ''
        if values['adjudicacion']:  # ADJUDICACION
            b_adj = self.env['proceso.adjudicacion_directa'].browse(values['adjudicacion'])
            if b_adj.normatividad == '1':  # 1 = federal
                var = 'Adjudicación Federal'
            else:  # estatal
                var = 'Adjudicación Estatal'
        else:  # LICITACION
            b_lic = self.env['proceso.licitacion'].browse(values['obra'])
            if b_lic.tipolicitacion == '1':  # 1 = LIC PUBLICA
                if b_lic.normatividad == '1':  # FEDERAL
                    var = 'Licitación Publica Federal'
                else:  # ESTATAL
                    var = 'Licitación Publica Estatal'
            else:  # LIC SIMPLIFICADA
                if b_lic.normatividad == '1':  # FEDERAL
                    var = 'Licitación Simplificada Estatal'
                else:  # ESTATAL
                    var = 'Licitación Simplificada Federal'

        b_expediente = self.env['control_expediente.control_expediente'].search(
            [('tipo_expediente.tipo_expediente', '=', var)],
            order='orden asc')  # BUSCAMOS LOS DOCUMENTOS DE EXPEDIENTES

        res = super(ElaboracionContratos, self).create(values)

        exp_contrato = self.env['control.expediente_contrato']

        datos_exp = {
            'contrato_id': res.id,
            'ejercicio': values['ejercicio'],
            'tipo_obra': values['tipo_obra'],
            'programa_inversion': values['programaInversion'],
        }
        xd2 = exp_contrato.create(datos_exp)  # CREAMOS EL FORMULARIO DE EXPEDIENTES

        numeracion = 0
        for vals in b_expediente:
            numeracion += 1
            datos = {'tabla_control':
                         [[0, 0,
                           {
                               'numeracion': numeracion,
                               'orden': vals.orden,
                               'nombre': vals.id,
                               'nombre_documento': vals.nombre,
                               'contrato_id': res.id,
                               'auxiliar': False,
                               'id_documento_categoria': None,
                               'auxiliar_comprimido': False,
                               'auxiliar_documentos_categoria': False,
                               'auxiliar_documentos_categoria2': False,
                               'p_id': None,
                               'responsable': vals.responsable.id,
                               'etapa': vals.etapa,
                               'categoria_documento': vals.categoria_documento.id,
                           }
                           ]]}
            tt = self.env['control.expediente_contrato'].browse(xd2.id)
            xd = tt.write(datos)  # ESCRIBIMOS LOS DOCUMENTOS DENTRO DEL FORMULARIO DE EXPEDIENTES

        libros = self.env['libros.blancos']
        datos = {
            'contrato': res.id,
            'comentarios_expediente': '',
            'programa_inversion': values['programaInversion'],
            'tipo_obra': values['tipo_obra'],
            'ejercicio': values['ejercicio'],
           
        }
        r = libros.create(datos)
        # libros_id = self.env['libros.blancos'].search(['id', '=', r])
        docs = self.env['expediente.documentos_revision'].search([])  # ("nombre_partida", "=", 'SIDUR-ED-15-039.8')
        for b_docs in docs:
            datos_d = ({
                'tabla_libros_blancos': [[0, 0, {
                    'contrato_id': res.id,
                    'numero_documento': b_docs.numero_documento,
                    'nombre_documento': b_docs.nombre_documento,
                    'etapa': b_docs.etapa,
                    'nombre_documento_m2o': b_docs.id,
                    'libros_blancos_id': r.id,
                    'programa_inversion': values['programaInversion'],
                    'tipo_obra': values['tipo_obra'],
                    'ejercicio': values['ejercicio'],
                }]]
            })
            re = r.write(datos_d)

        return res
        


    # CONTEXT DESCARGAR ARCHIVO
    @api.multi
    def imprimir_accion(self):
        original_url = "http://sidur.galartec.com/docx/CONTRATO/id/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    count_convenios_modif = fields.Integer(compute="contar_covenios")

    @api.one
    def contar_covenios(self):
        count = self.env['proceso.convenios_modificado'].search_count([('nombre_contrato', '=', self.contrato)])
        self.count_convenios_modif = count

    @api.multi
    def convenios_views(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_convenios_modificados_tree')
        view2 = self.env.ref('proceso_contratacion.proceso_convenios')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'tree',
            'context': {'search_default_contrato_contrato': self.id,
                        'default_contrato_contrato': self.id,
                        'default_nombre_contrato': self.contrato},
            'view_id': False,
            'views': [
                (view.id, 'tree'),
                (view2.id, 'form'),
            ],
        }

    # METODO PARA CALCULAR EL IMPORTE DEL CONTRATO
    @api.one
    @api.depends('contrato_partida_adjudicacion', 'contrato_partida_licitacion')
    def importeT(self):
        if self.iva_frontera:
            iva = 0.08
        else:
            iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        if self.adjudicacion:
            suma = 0
            for i in self.contrato_partida_adjudicacion:
                resultado = i.monto_partida
                suma += resultado
            self.impcontra = suma
            self.impcontra_iva = suma * float(iva)
            self.total_civa = self.impcontra_iva + suma
        else:
            suma = 0
            for i in self.contrato_partida_licitacion:
                resultado = i.monto_partida
                suma += resultado
            self.impcontra = suma
            self.impcontra_iva = suma * float(iva)
            self.total_civa = self.impcontra_iva + suma

    # VALIDACIONES DE FECHAS
    @api.onchange('fechatermino')
    @api.depends('fechatermino', 'fechainicio')
    def onchange_fechatermino(self):
        if str(self.fechatermino) < str(self.fechainicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la fecha de inicio, '
                                     'por favor seleccione una fecha posterior')
        else:
            return False

    @api.onchange('fechainicio')
    @api.depends('fechatermino', 'fechainicio')
    def onchange_fechainicio(self):
        if str(self.fechatermino) < str(self.fechainicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha posterior a la de termino, '
                                     'por favor seleccione una fecha anterior')
        else:
            return False

    # VALIDACIONES DE RECURSOS
    '''@api.onchange('impcontra')
    def onchange_recursos(self):
        if self.saldo < 0:
            raise exceptions.Warning('No se cuenta con los recursos suficientes')
        else:
            return False'''

    # METODO PARA INYECTAR ANEXOS @api.depends('adjudicacion', 'obra')
    @api.multi
    def llenar_anexo(self):
        # adujidcacion
        if self.tipo_contrato == '2':
            for i in self.contrato_partida_adjudicacion:
                contrato = self.env['proceso.elaboracion_contrato']

                b_anexo_adju = self.env['autorizacion_obra.anexo_tecnico'].search([('id', '=', i.recursos.id)])

                datos_recursos = {
                    'anexos': [[4,  b_anexo_adju.id, {
                    }]]}

                recurso = contrato.browse(self.id)

                recursos_tabla = recurso.update(datos_recursos)

        # licitacion
        elif self.tipo_contrato == '1':
            for i in self.contrato_partida_licitacion:
                contrato = self.env['proceso.elaboracion_contrato']
                b_anexo_adju = self.env['autorizacion_obra.anexo_tecnico'].search([('id', '=', i.recursos.id)])
                datos_recursos = {
                    'anexos': [[4, b_anexo_adju.id, {
                    }]]}
                recurso = contrato.browse(self.id)
                recursos_tabla = recurso.update(datos_recursos)

    @api.depends('total_recurso_aut', 'total_contratado')
    def saldo_total(self):
        for rec in self:
            rec.update({
                'saldo': rec.total_recurso_aut - rec.total_contratado
            })

    @api.depends('impcontra')
    def contratado_total(self):
        for rec in self:
            rec.update({
                'total_contratado': rec.total_civa
            })

    @api.depends('impcontra', 'convenios_escalatorias')
    def contratado_total_modi(self):
        for rec in self:
            rec.update({
                'total_contratado': rec.total_civa + rec.convenios_escalatorias
            })

    # CALCULAR EL RECURSO TOTAL DE LOS ANEXOS
    @api.multi
    def recurso_total(self):
        for rec in self:
            rec.update({
                'total_recurso_aut': rec.recurso_autorizado - rec.importe_cancelado
            })

    # IDS DE REFERENCIA DE LA ADJUDICACION O LICITACION PARA METODO DE BUSCAR CONTRATO EN PARTIDAS
    id_ad = fields.Integer(string="ID DE LA ADJUDICACION RELACION", related="adjudicacion.id")

    id_lic = fields.Integer(string="ID DE LA LICITACION RELACION", related="obra.id")

    programaInversion = fields.Many2one('generales.programas_inversion', store=True)
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra", store=True)

    # METODO DE LAS PARTIDAS ADJUDICACION
    @api.multi
    @api.onchange('adjudicacion')  # if these fields are changed, call method
    def check_change_adjudicacion(self):
        adirecta_id = self.env['proceso.adjudicacion_directa'].browse(self.adjudicacion.id)
        self.update({
            'contrato_partida_adjudicacion': [[5]]
        })
        cont = 0

        b_partida = self.env['partidas.partidas'].search_count([('id_contrato_sideop', '=', False)])

        numero_id = 2000 + (b_partida + 1)
        nombre_partida = str(self.contrato) + '.' + str(numero_id)

        if self.obra: # licitacion
            if self.obra.tipolicitacion == '1': # publica
                adj = 'LP' # simplificada
            else:

                adj = 'LS'
        else: # adjudicacion
            adj = 'AD'

        for partidas in adirecta_id.programar_obra_adjudicacion:
            self.programaInversion = partidas.programaInversion
            self.tipo_obra = partidas.obra.obra_planeada.tipoObra
            cont = cont + 1
            self.update({
                'contrato_partida_adjudicacion': [[0, 0, {
                                                          'recursos': partidas.recursos,
                                                          'obra': partidas.obra,
                                                          'programaInversion': partidas.programaInversion,
                                                          'municipio': partidas.obra.obra_planeada.municipio.id,
                                                          # SE QUEDARAN SIEMPRE COMO EL MONTO ORIGINAL
                                                          'monto_partida': partidas.monto_partida,
                                                          'iva_partida': partidas.iva_partida,
                                                          'total_partida': partidas.total_partida,
                                                          # ESTAN SUJETOS A CAMBIO POR CONVENIO
                                                          'total': partidas.monto_partida,
                                                          'total_iva': partidas.iva_partida,
                                                          'total_civa': partidas.total_partida,

                                                          'nombre_contrato': self.contrato,
                                                          'contratista': self.contratista.id,
                                                          'nombre_partida': nombre_partida,
                                                          'ejercicio': self.ejercicio.id,
                                                          'odoo_user_admin': 2,
                                                          'odoo_user_oscar': 623,
                                                          'odoo_user_fabiola': 555,
                                                          'odoo_user_celaya': 551,
                                                          'fecha_pago_anticipo': None,
                                                          'p_id': cont,
                                                          'tipo_adjudicacion': adj,
                                                          }]]
                     })

    # ACTUALIZAR DATOS DE LA TABLA FALTANTES
    @api.multi
    @api.onchange('contrato')
    def actualizar_m2m(self):
        if not self.contrato:
            pass
        else:
            b_partida = self.env['partidas.partidas'].search_count([('id_contrato_sideop', '=', False)])

            if self.adjudicacion.contratado == 1 or self.obra.contratado == 1:
                pass
            else:
                numero_id = 2000 + (b_partida + 1)
                nombre_partida = str(self.contrato) + '.' + str(numero_id)
                if self.contrato_partida_licitacion:
                    for rec in self.contrato_partida_licitacion:
                        rec.update({
                            'nombre_contrato': self.contrato,
                            'nombre_partida': nombre_partida
                        })
                else:
                    for rec in self.contrato_partida_adjudicacion:
                        rec.update({
                            'nombre_contrato': self.contrato,
                            'nombre_partida': nombre_partida
                        })

    # METODO DE LAS PARTIDAS LICITACION
    @api.multi
    @api.onchange('obra')  # if these fields are changed, call method
    def check_change_licitacion(self):
        self.update({
            'contrato_partida_licitacion': [[5]]
        })

        b_eve = self.env['proceso.eventos_licitacion'].search(
            [('numerolicitacion_evento.id', '=', self.obra.id)])

        acum = 0
        b_partida = self.env['partidas.partidas'].search_count([('id_contrato_sideop', '=', False)])

        if self.obra: # licitacion
            if self.obra.tipolicitacion == '1': # publica
                adj = 'LP' # simplificada
            else:

                adj = 'LS'
        else: # adjudicacion
            adj = 'AD'
            
        numero_id = 2000 + (b_partida + 1)
        nombre_partida = str(self.contrato) + '.' + str(numero_id)
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        for x in b_eve.contratista_propuesta:
            acum += 1
            if int(x.posicion) == 1:
                acumx = 0
                cont = 0
                for o in b_eve.contratista_propuesta[int(acum)-1].programar_obra_licitacion2:
                    self.programaInversion = o.programaInversion
                    self.tipo_obra = o.obra.obra_planeada.tipoObra
                    ivax = o.monto_partida * float(iva)
                    total = o.monto_partida + ivax
                    acumx += 1
                    cont = cont + 1
                    self.update({
                        'contrato_partida_licitacion': [[0, 0, {'recursos': o.recursos,
                                                                'programaInversion': o.programaInversion,
                                                                'obra': o.obra,
                                                                'municipio': o.obra.obra_planeada.municipio.id,
                                                                'licitacion': self.obra.numerolicitacion ,
                                                                # MONTOS ORIGINALES
                                                                'monto_partida': o.monto_partida,
                                                                'iva_partida': ivax,
                                                                'total_partida': total,
                                                                # MONTOS SUJETOS A CAMBIO POR CONVENIO
                                                                'total': o.monto_partida,
                                                                'total_iva': ivax,
                                                                'total_civa': total,

                                                                'contratista': self.contratista.id,
                                                                'nombre_contrato': self.contrato,
                                                                'nombre_partida': nombre_partida,
                                                                'p_id': cont,
                                                                'odoo_user_admin': 2,
                                                                'odoo_user_oscar': 623,
                                                                'odoo_user_fabiola': 555,
                                                                'odoo_user_celaya': 551,
                                                                'fecha_pago_anticipo': None,
                                                                'ejercicio': self.ejercicio.id,
                                                                'tipo_adjudicacion': adj,
                                                                }]]
                    })
            elif int(x.posicion) is False:
                print('NO se encontro ganador')

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def contar(self):
        count = self.env['proceso.finiquitar_anticipadamente'].search_count([('contrato', '=', self.id)])
        self.contar_finiquito = count

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def contar2(self):
        count = self.env['proceso.convenios_modificado'].search_count([('contrato_contrato', '=', self.id)])
        self.contar_convenio = count

    # CONVENIOS MODIFICATORIOS METODOS DE ABRIR VENTANA EN MODO NEW Y EN TREE VIEW
    @api.multi
    def conveniosModificados1(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios Modificatorios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'form,tree',
            'target': 'new',
        }

    @api.multi
    def conveniosModificados2(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios Modificatorios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'tree,form',
        }

    # FINIQUITAR CONTRATO METODOS DE ABRIR VENTANA EN MODO NEW Y EN TREE VIEW
    @api.multi
    def finiquitarContrato1(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Finiquitar Contrato Anticipadamente',
            'res_model': 'proceso.finiquitar_anticipadamente',
            'view_mode': 'form,tree',
            'target': 'new',
        }

    @api.multi
    def finiquitarContrato2(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Finiquitar Contrato Anticipadamente',
            'res_model': 'proceso.finiquitar_anticipadamente',
            'view_mode': 'tree,form',
        }

    #
    @api.multi
    def Seleccion(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccion de Obra',
            'res_model': 'proceso.elaboracion_contrato',
            'view_type': 'form',
            'target': 'new',
        }


class AnexosAuxiliar(models.Model):
    _name = 'proceso.anexos'

    id_contrato = fields.Many2one('proceso.elaboracion_contrato')

    name = fields.Many2one('autorizacion_obra.oficios_de_autorizacion')

    fecha_de_recibido = fields.Date(string='Fecha de recibido', related="name.fecha_de_recibido")
    fecha_de_vencimiento = fields.Date(string='Fecha de vencimiento', related="name.fecha_de_vencimiento")

    concepto = fields.Many2one('registro.programarobra')
    claveobra = fields.Char(string='Clave de obra')
    clave_presupuestal = fields.Char(string='Clave presupuestal')
    federal = fields.Float(string='Federal')
    estatal = fields.Float(string='Estatal')
    municipal = fields.Float(string='Municipal')
    otros = fields.Float(string='Otros')
    federalin = fields.Float(string='Federal')
    estatalin = fields.Float(string='Estatal')
    municipalin = fields.Float(string='Municipal')
    otrosin = fields.Float(string='Otros')
    total = fields.Float()
    cancelados = fields.Integer()
    total_ca = fields.Float(string='Cancelado')
    total1 = fields.Float(string="Total")
    totalin = fields.Float(string="Indirectos")

    total_at = fields.Float()


class UnidadResponsableEjecucion(models.Model):
    _name = 'proceso.unidad_responsable'

    id_sideop = fields.Integer()
    name = fields.Char('Descripción:')


class Fianza(models.Model):
    _name = 'proceso.fianza'

    select_tipo_fianza = [('1', 'Cumplimiento'), ('2', 'Calidad/Vicios Ocultos'), ('3', 'Responsabilidad Civil'),
                          ('4', 'Ninguno')]
    tipo_fianza = fields.Selection(select_tipo_fianza, string="Tipo Fianza", default="4", )
    numero_fianza_fianzas = fields.Char(string="Numero Fianza", )
    monto = fields.Float(string="Monto", )
    fecha_fianza_fianzas = fields.Date(string="Fecha Fianza", )
    afianzadora_fianzas = fields.Char(string="Afianzadora", )


class FiniquitarContratoAnticipadamente(models.Model):
    _name = "proceso.finiquitar_anticipadamente"

    @api.one
    def nombre(self):
        self.contrato_id = self.id

    contrato_id = fields.Char(compute="nombre", store=True)
    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Numero Contrato:', readonly=True)

    fecha = fields.Date(string="Fecha:")
    referencia = fields.Char(string="Referencia:")
    observaciones = fields.Text(string="Observaciones:")


