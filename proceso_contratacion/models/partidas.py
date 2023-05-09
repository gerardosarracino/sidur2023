from odoo import models, fields, api, exceptions
from datetime import date, datetime
from datetime import datetime
import calendar
import datetime

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


# CLASE AUXILIAR DE PARTIDAS LICITACION
class PartidasLicitacion(models.Model):
    _name = 'partidas.licitacion'

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio",
                                related="obra.obra_planeada.ejercicio")
                                
    id_sideop = fields.Integer()
    id_sideop_partida = fields.Integer()

    # id_licitacion = fields.Many2one(comodel_name="proceso.licitacion")
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos',
                               domain="['&', ('concepto.obra_adj_lic', '=', False), ('p_inv2.id', '=', programaInversion)]", required=True)

    @api.multi
    @api.onchange('recursos')
    def b_recurso(self):
        if not self.recursos:
            pass
        else:
            b_r2 = self.env['autorizacion_obra.anexo_tecnico'].search(
                [('concepto.id', '=', self.recursos.concepto.id)])[0]
            self.obra = b_r2.concepto.id

    obra = fields.Many2one('registro.programarobra', required=True)
    programaInversion = fields.Many2one('generales.programas_inversion')
    monto_partida = fields.Float(string="Monto", required=True)
    iva_partida = fields.Float(string="Iva", compute="iva")
    total_partida = fields.Float(string="Total", compute="sumaPartidas")
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # METODO CALCULAR TOTAL PARTIDA
    @api.one
    def sumaPartidas(self):
        for rec in self:
            rec.update({
                'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida
            })

    # CALCULAR EL IVA TOTAL
    @api.one
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })


# CLASE AUXILIAR DE PARTIDAS ADJUDICACION
class PartidasAdjudicacion(models.Model):
    _name = 'partidas.adjudicacion'

    id_sideop_adjudicacion = fields.Integer('ID SIDEOP')
    id_sideop_partida = fields.Integer('ID SIDEOP part')

    id_adjudicacion = fields.Many2one('proceso.adjudicacion_directa')
    
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')

    @api.multi
    @api.onchange('obra')
    def b_recurso(self):
        if not self.obra:
            pass
        else:
            b_r2 = self.env['autorizacion_obra.anexo_tecnico'].search([('concepto.id', '=', self.obra.id)])
            for i in b_r2:
                self.recursos = i.id

    obra = fields.Many2one('registro.programarobra', domain="['&',('obra_adj_lic', '=', False),('programaInversion', '=', programaInversion)]", required=True)

    @api.model
    def create(self, values):
        _search_cove = self.env['registro.programarobra'].search([("id", "=", values['obra'])])
        for vals2 in _search_cove:
            b_obra = self.env['registro.programarobra'].browse(vals2['id'])
            b_obra.write({'obra_adj_lic': True})
        return super(PartidasAdjudicacion, self).create(values)

    programaInversion = fields.Many2one('generales.programas_inversion')
    monto_partida = fields.Float(string="Monto", required=True)
    iva_partida = fields.Float(string="Iva", compute="iva", store=True)
    total_partida = fields.Float(string="Total", compute="sumaPartidas", store=True)
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva", store=True)

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    @api.depends('monto_partida')
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # METODO CALCULAR TOTAL PARTIDA
    @api.one
    @api.depends('monto_partida')
    def sumaPartidas(self):
        for rec in self:
            rec.update({
                'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida
            })

    # CALCULAR EL IVA TOTAL
    @api.one
    @api.depends('monto_partida')
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })

    @api.model
    def create(self, values):
        b_obrap = self.env['registro.programarobra'].browse(values['obra'])
        b_obrap.write({'obra_adj_lic': True})
        return super(PartidasAdjudicacion, self).create(values)

# CLASE DE LAS PARTIDAS Y CONCEPTOS CONTRATADOS
class Partidas(models.Model):
    _name = 'partidas.partidas'
    _rec_name = "nombre_partida"
    _inherit = 'mail.thread'

    odoo_user_admin = fields.Many2one('res.users', string='Residente obra:', store=True) # compute="user_admin"
    odoo_user_oscar = fields.Many2one('res.users', string='Residente obra:', store=True) # compute="user_admin"
    odoo_user_fabiola = fields.Many2one('res.users', string='Residente obra:', store=True) # compute="user_admin"
    odoo_user_celaya = fields.Many2one('res.users', string='Residente obra:', store=True) # compute="user_admin"
    
    super_residente = fields.Many2many('res.users', string='Ver todas las obras como residente', )

    clave_pep = fields.Char(related="obra.obra_planeada.numero_obra")
    oficio_autorizacion = fields.Char(related="recursos.name.name")

    actualizar_onchange = fields.Boolean(' PRUEBA ')
    actualizar_script = fields.Boolean(' PRUEBA ')

    licitacion = fields.Char(string="Licitacion")

    # IMPORTACION
    # NUNCA BORRAR, NECESARIO PARA SACAR NUMERO DE CONTRATO
    id_contrato_sideop = fields.Char(string="num_contrato SIDEOP", required=False, ) # NUM_CONTRATO SIDEOP
    # TERMINA IMPORTACION

    numero_contrato = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Numero de Contrato")  # compute="contrato_metodo"

    @api.model
    def create(self, values):
        b_contrato = self.env['proceso.elaboracion_contrato'].search([('contrato', '=', values['nombre_contrato'])])
        values['numero_contrato'] = b_contrato.id
        estado = self.env['semaforo.estado_obra_lista'].search([('estado_obra', '=', 'Nueva')])
        values['estado_obra_m2o'] = estado.id
        values['tipo_estado_obra'] = 'Nueva'
        search_usuarios = self.env['res.users'].search([('super_residente', '!=', False)])
        res = super(Partidas, self).create(values)
        for i in search_usuarios:
            datos = {'super_residente': [[4, i.id, {}]]}
            xd = res.update(datos)
        return res

    radio_adj_lic = [('1', "Licitación"), ('2', "Adjudicación")]
    tipo_contrato = fields.Selection(radio_adj_lic, string="Tipo de Contrato", store=True, related="numero_contrato.tipo_contrato")

    # OBRA A LA QUE PERTENECE LA PARTIDA
    obra = fields.Many2one('registro.programarobra', )
    # PROGRAMA DE INVERSION
    programaInversion = fields.Many2one('generales.programas_inversion', string="Programa de Inversión", ) # related="obra.programaInversion"

    # RECURSOS LICITACION
    recursos = fields.Many2one('autorizacion_obra.anexo_tecnico', 'Recursos')

    # EL OBJETO ES LA DESCRIPCION DE LA OBRA EN EL CONTRATO
    objeto = fields.Text(string="Objeto", related="numero_contrato.name")

    @api.multi
    def decargar_catalogo_excel(self):
        url = "/Conceptos/?id=" + str(self.id)
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }
        
    @api.multi
    def imprimir_accion_concepto(self):
        return {"type": "ir.actions.act_url", "url": "http://sidur.galartec.com:9001/conceptos/index.php?id=" + str(self.id), "target": "new", }

    @api.multi
    def descargar_ficha_tecnica(self):
        url = "/FICHA_TECNICA/FICHA_TECNICA/?id=" + str(self.id)
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    # CATALOGO DE CONCEPTOS
    conceptos_partidas = fields.Many2many('proceso.conceptos_part', required=True)
    ordenes_conceptos = fields.Many2many('ordenes.conceptos_espejo')  # ORDENES DE CAMBIO CONCEPTOS EN ESPEJO
    
    # CONCEPTOS MODIFICADOS PARA EL HISTORIAL DE CATALOGOS AUN NO IMPLEMENTADO
    # conceptos_modificados = fields.Many2many('proceso.conceptos_modificados', required=True)

    justificacion = fields.Text('Justificación de Modificación')
    select_tipo = [('1', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:")

    # name = fields.Many2one('proceso.elaboracion_contrato', readonly=True)

    # MONTOS ORIGINALES DEL CONTRATO
    monto_partida = fields.Float(string="Monto", store=True) # ES EL MONTO DE LA PARTIDA SIN IVA
    iva_partida = fields.Float(string="Iva", store=True) 
    total_partida = fields.Float(string="Total", store=True) 

    @api.multi
    @api.onchange('monto_partida')
    def calcular_monto(self):
        self.iva_partida = self.monto_partida * self.b_iva
        self.total_partida = self.monto_partida + self.iva_partida

    # TOTAL DE LA PARTIDA MONTO CONTRATADO SIN IVA, ESTE USA SIDEOP
    # total con convenio
    monto_sin_iva_modi = fields.Float(string="Total Modificado", compute="nuevo_total_partida")
    # TOTAL DE LA PARTIDA CONTIENE EL MONTO ORIGINAL CONTRATADO MAS SUMATORIA DE MONTOS POR CONVENIO

    total = fields.Float(string="Monto Total Contratado:", digits=(12,2), store=True)
    total_iva = fields.Float(string="Iva Total Contratado:", digits=(12,2), store=True)
    total_civa = fields.Float(string="Monto Total Contratado cIva:", digits=(12,2), store=True)
    
    @api.multi
    @api.onchange('total')
    def calcular_monto_modif(self):
        self.total_iva = self.total * self.b_iva
        self.total_civa = self.total + self.total_iva

    # BUSQUEDA DE CONVENIOS PARA ESTA PARTIDA
    # FIELD CON EL TOTAL DEL CONVENIO INCLUYE LA SUMA Y RESTA
    convenios_ = fields.Float(string="", compute="nuevo_total_partida"  ) # compute="b_convenios"

    # APLICA EL CALCULO DEL CONVENIO AL MONTO DEL CONTRATO DE LA PARTIDA SI ES QUE EXISTE UNO
    @api.one
    def nuevo_total_partida(self):
        _search_cove_c = self.env['proceso.convenios_modificado'].search_count([("nombre_contrato", "=", self.nombre_contrato)])
        _search_cove = self.env['proceso.convenios_modificado'].search([("nombre_contrato", "=", self.nombre_contrato)])
        acum = 0
        acum2 = 0
        for i in _search_cove:
            if i.tipo_monto == 'AM':
                acum = acum + i.monto_importe
            elif i.tipo_monto == 'RE':
                acum2 = acum2 + i.monto_importe
            ampliacion = acum
            reduccion = acum2
            total = ampliacion - reduccion
            self.convenios_ = total

        if _search_cove_c == 0:
            self.monto_sin_iva_modi = 0
        else:
            self.monto_sin_iva_modi = self.monto_partida + self.convenios_


    # TOTAL DEL MONTO DE LOS CATALGOS
    total_catalogo = fields.Float(string="Monto Total del Catálogo", compute="SumaImporte", required=True, digits=(12,2))
    # DIFERENCIA ENTRE EL MONTO TOTAL Y EL MONTO DEL CONTRATO SIN IVA
    diferencia = fields.Float(string="Diferencia:", compute="Diferencia", digits=(12,2))

    # DEDUCCIONES
    # deducciones = fields.Many2many('generales.deducciones', string="Deducciones:")

    # ANTICIPOS
    # ANTICIPOS
    fecha_anticipos = fields.Date(string="Fecha Anticipo", )
    fecha_pago_anticipo = fields.Date(string="Fecha de Pago del Anticipo", )

    porcentaje_anticipo = fields.Float(string="Anticipo Inicio", store=True )
    anticipo_material = fields.Float(string="Anticipo Material", store=True)
    total_anticipo_porcentaje = fields.Float(string="Total Anticipo", compute="total_anticipo_suma", store=True)
    importe = fields.Float(string="Importe Contratado", digits=(12, 2))
    anticipo_a = fields.Float(string="Anticipo", store=True, digits=(12, 2))
    iva_anticipo = fields.Float(string="I.V.A", store=True, digits=(12, 2))

    total_anticipo = fields.Float(string="Total Anticipo", store=True, digits=(12, 2))

    @api.one
    @api.depends('fecha_anticipos','porcentaje_anticipo', 'anticipo_material')
    def total_anticipo_suma(self):
        self.total_anticipo_porcentaje = self.porcentaje_anticipo + self.anticipo_material

    numero_fianza = fields.Char(string="# Fianza", )
    afianzadora = fields.Char(string="Afianzadora", )
    fecha_fianza = fields.Date(string="Fecha Fianza", )
    anticipada = fields.Boolean(string="Anticipada", compute="anticipada_Sel")

    # BUSCAR LOS PORCENTAJES DEL ANTICIPO DESDE LA ADJUDICACION O LICITACION RESPECTIVAMENTE
    @api.multi
    @api.onchange('fecha_anticipos')
    def b_anticipo(self):
        b_contrato = self.env['proceso.elaboracion_contrato'].search([('id', '=', self.numero_contrato.id)])
        if b_contrato.tipo_contrato == '2':
            self.porcentaje_anticipo = float(b_contrato.adjudicacion.anticipoinicio) / 100
            self.anticipo_material = float(b_contrato.adjudicacion.anticipomaterial) / 100
        elif b_contrato.tipo_contrato == '1':
            self.porcentaje_anticipo = float(b_contrato.obra.anticipoinicio) / 100
            self.anticipo_material = float(b_contrato.obra.anticipomaterial) / 100
    # ////////////// TERMINA ANTICIPOS

    # CONVENIOS MODIFICATORIOS
    convenios_modificatorios = fields.Many2many('proceso.convenios', string="Conv. Modificatorios")
    referencia_convenio = fields.Char('Referencia Convenio') # c1, c2, c3 etc
    tipo_adjudicacion = fields.Char('Tipo de Adjudicacion') # LP, LS, AD

    # RESIDENCIA
    residente_obra = fields.Many2many('res.users', 'name', string='Residente obra:', store=True)

    supervision_externa = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:")
    director_obras = fields.Char('Director de obras:')
    puesto_director_obras = fields.Text('Puesto director de obras:')
    representante_legal = fields.Text('Representante Legal')

    # RUTA CRITICA
    ruta_critica = fields.Many2many('proceso.rc')
    ruta_critica_frentes = fields.One2many('proceso.frente', 'id_partida')

    avance_programado_fecha = fields.Float(store=True)
    fecha_simulacion = fields.Date('Seleccionar Fecha de la Simulacion de Avance Programado')

    @api.multi
    def agregar_frente(self):
        print('frente')
        # search = self.env['project.project'].search([('id', '=', self.project_id.id)])
        form = self.env.ref('supervision_obra.concepto_ruta_critica_frente_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ruta critica',
            'res_model': 'proceso.rc',
            'view_mode': 'form',
            'target': 'new',
            # 'domain': [('proyecto_id', '=', self.project_id.id)],
            # 'view_id': view.id,
            'context': {'default_id_partida': self.id},
            'views': [
                (form.id, 'form'),
            ],
            # 'res_id': search.id,  # (view.id, 'form')
        }

    @api.multi
    @api.onchange('fecha_simulacion')
    def porProgramado(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self._origin.id)])
        date_format = "%Y/%m/%d"
        date_format2 = "%Y-%m-%d"
        today = self.fecha_simulacion
        hoy = str(today.strftime(date_format))

        fecha_hoy = today

        if len(hoy) == '':
            Prog_Del = None
        else:
            Prog_Del_ = str(today)
            Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + \
                       Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

        # fecha_hoy = datetime.strptime(str(fecha_act), date_format2)

        for u in b_programa.programa_contratos:
            fecha_termino_pp = u.fecha_termino

            if str(fecha_termino_pp) == 'False':
                print('NO HAY FECHA DE TERMINO')
            else:
                fecha_termino_contrato = fecha_termino_pp

                acumulado = 0
                cont = 0
                porcentajeProgramado = 0
                for i in b_programa.programa_contratos:
                    cont += 1
                    
                    if fecha_hoy > fecha_termino_contrato:
                        porcentajeProgramado = 100.00
                        self.avance_programado_fecha = porcentajeProgramado

                    # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                    if fecha_hoy <= fecha_termino_contrato:
                        # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                        fechainicioprog = datetime.datetime.strptime(str(i.fecha_inicio), date_format2)
                        if str(fechainicioprog) <= str(fecha_hoy):
                            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                            fechainicioprog = datetime.datetime.strptime(str(i.fecha_inicio), date_format2)
                            _fecha_actual = datetime.datetime.strptime(str(today), date_format2)
                            r = _fecha_actual - fechainicioprog
                            dias_trans = r.days + 1
                            diasest = calendar.monthrange(i.fecha_inicio.year, i.fecha_inicio.month)[1]
                            dias_del_mes = diasest  # r2.days + 1
                            if dias_del_mes == 0:
                                dias_del_mes = 1
                            # MONTO ACUMULADO DE PROGRAMAS
                            acumulado += i.monto
                            ultimo_monto = i.monto

                            # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                            # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                            # EL TOTAL DEL PROGRAMA * 100
                            importe_diario = ((((i.monto / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto))
                                              / b_programa.total_programa) * 100
                            if importe_diario > 100:
                                rr = 100
                            elif importe_diario <= 100:
                                rr = importe_diario
                            porcentajeProgramado = rr
                            self.avance_programado_fecha = rr
                        else:
                            pass

    comentarios_supervision = fields.Many2many('comentario.supervision', string='Comentarios de Supervision')
    estado_supervision = fields.Selection([('Activa', "Activa"), ('Terminada', "Terminada")], string="Estado de la Supervision", default="Activa")
    
    @api.multi
    def toda_galeria(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.galeria_view_kanban')
        # search = self.env['proceso.subirgaleria'].search([('informe_avance.id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ver Galeria',
            'res_model': 'proceso.subirgaleria',
            'view_mode': 'kanban',
            'context': {'search_default_partida': self.id},
            'view_id': view.id,
        }

    @api.multi
    def convenios_views(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_convenios_modificados_tree')
        view2 = self.env.ref('proceso_contratacion.proceso_convenios')
        # search = self.env['proceso.subirgaleria'].search([('informe_avance.id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenios',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'tree',
            'context': {'search_default_contrato_contrato': self.numero_contrato.id, 'default_contrato': self.id,
                        'default_contrato_contrato': self.numero_contrato.id, 'default_nombre_contrato': self.nombre_contrato},
            'view_id': False,
            'views': [
                (view.id, 'tree'),
                (view2.id, 'form'),
            ],
        }

    total_ = fields.Float('Total % Ruta critica', store=True) # compute='suma_importe'
    # Contador de convenios por obra
    count_convenios_modif = fields.Integer(compute="contar_covenios")

    # VISTA DE INFORMACION DE LA PARTIDA
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio",)
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo", related="obra.obra_planeada.tipoObra")
    municipio = fields.Many2one('generales.municipios', 'Municipio', )
    estado = fields.Many2one('generales.estado', 'Municipio', related="obra.obra_planeada.estado")
    localidad = fields.Text(string="Localidad", readonly="True", related="obra.obra_planeada.localidad")
    fecha = fields.Date(string="Fecha", related="numero_contrato.fecha")
    fechainicio = fields.Date(string="Fecha de Inicio", related="numero_contrato.fechainicio")
    fechatermino = fields.Date(string="Fecha de Termino", related="numero_contrato.fechatermino")

    supervisionexterna1 = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:",
                                          related="numero_contrato.supervisionexterna1")
    # RELACION CONTRATISTA
    contratista = fields.Many2one('contratista.contratista', store=True)

    # NOMBRE DE LA PARTIDA = AL DEL CONTRATO.ID
    # NOMBRE DEL CONTRATO = CONTRATO
    nombre_contrato = fields.Char(string="Nombre contrato", required=False, )
    nombre_partida = fields.Char(string="Nombre partida", )

    # INICIO FINIQUITO #
    fecha1 = fields.Date(string="Fecha de aviso de terminación de los trabajos")
    fecha2 = fields.Datetime(string="Fecha y hora verificación de la terminación de los trabajos")
    numero = fields.Char(string="Número bitácora del contrato")
    nota1 = fields.Text(string="Nota de bitácora aviso terminación")
    fecha3 = fields.Date(string="Fecha nota bitácora")
    fecha4 = fields.Date(string="Fecha de aviso de terminación de trabajos")
    fecha5 = fields.Date(string="Fecha de inicio Real del contrato")
    fecha6 = fields.Date(string="Fecha de termino real del contrato")
    fecha7 = fields.Datetime(string="Fecha y hora programada del acta de recepción de los trabajos")
    fecha8 = fields.Datetime(string="Fecha y hora entrega de la obra")
    fecha9 = fields.Datetime(string="Fecha y hora finiquito")
    fecha10 = fields.Datetime(string="Fecha y hora acta cierre administrativo")
    fecha11 = fields.Datetime(string="Fecha y hora acta de extinción de derechos")
    description = fields.Text(string="Descripción de los trabajos")
    creditosContra = fields.Char(string="Créditos en contra del contratista al finalizar la obra")

    @api.multi
    def reporte_finiquito(self):
        original_url = "http://sidur.galartec.com/docx/FINIQUITO/id/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }
    # FIN FINIQUITO #   

    #Galeria
    @api.multi
    def galeria_imagenes(self):
        original_url = "http://sidur.galartec.com:4000/galeria/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

       

    # USADA COMO AUXILIAR
    p_id = fields.Integer('VARIABLE AUXILIAR')

    # RESTRICCION DEL PROGRAMA, SI NO HAY PROGRAMA NO PERMITE REGISTRAR UNA ESTIMACION
    verif_programa = fields.Boolean(string="", compute="programa_verif")
    # VALOR DEL IVA TRAIDO DESDE CONFIGURACION
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")

    iva_frontera = fields.Boolean(string="Es iva de frontera?", store=True)

    # CONTAR REGISTROS DE ESTIMACIONES
    contar_estimaciones = fields.Integer(compute='ContarEstimaciones', string="PRUEBA")

    # M2M PARA PODER HACER REPORTE DE ESTADO DE CUENTA DE ESTIMACIONES MAS SU METODO
    esti = fields.Many2many(comodel_name="control.estimaciones")

    # CONTROL DE EXPEDIENTES
    tabla_control = fields.One2many('control.expediente', 'p_id')
    tabla_libros_blancos = fields.Many2many('expediente.libros_blancos', string='Revision de Expedientes', store=True)
    
    unidadresponsableejecucion = fields.Many2one('proceso.unidad_responsable', string="Unidad responsable de su ejecución", related="numero_contrato.unidadresponsableejecucion")

    porcentaje_existencia = fields.Float(string="% Existencia", store=True)

    @api.multi
    @api.onchange('tabla_libros_blancos')
    def onchange_method(self):
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

    # GALERIA DE IMAGENES DE AVANCE FINANCIERO
    galleria = fields.Many2many('avance.avance_fisico', nolabel=True)

    # ESTIMACION ENLACE
    estimacion_id = fields.Char(compute="nombre", store=True)

    _url = fields.Char(compute="_calc_url")

    # SEMAFORO
    residente_x = fields.Char('Residente', readonly=True, store=True)
    residentes_obra = fields.Many2many('partida.residente', string='new residentes', store=True)
    monto_del_programa = fields.Float(string="",  compute="_monto_programa" )

    @api.multi
    @api.onchange('residente_obra')
    def residente_char(self):
        ac = ""
        c = 0
        for i in self.residente_obra:
            print(i.name)
            c += 1
            if c > 1:
                ac += "," + str(i.name)
            else:
                ac += str(i.name)
        self.residente_x = ac

    fecha_inicio_convenida = fields.Date('Fecha Inicio Convenida', ) # compute="_monto_programa"
    fecha_termino_convenida = fields.Date('Fecha Termino Convenida', ) # compute="_monto_programa"

    semaforo_tags = fields.Many2many(comodel_name="semaforo.categorias", string="Tags")

    @api.one
    def _monto_programa(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.id)])
        self.monto_del_programa = b_programa.total_programa
        for i in self.convenio_semaforo:
            if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                self.fecha_inicio_convenida = i.plazo_fecha_inicio
                self.fecha_termino_convenida = i.plazo_fecha_termino
            else:
                pass

    estado_obra = fields.Many2many('semaforo.estado_obra')
    
    estado_actividad = fields.Many2many('semaforo.actividad')

    @api.multi
    def estado_obra_semaforox(self):
        view = self.env.ref('semaforo.estado_obra_semaforo_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estado de Obra',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    comentario_obra = fields.Many2many(comodel_name="semaforo.comentarios_obra", string="Comentarios de Obra", )

    @api.multi
    def agregar_comentario(self):
        view = self.env.ref('semaforo.comentario_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comentario',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    @api.multi
    def descargar_pp(self):
        original_url = "/ppt/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    select_estado = [('Terminado', 'Terminado'), ('En Ejecucion', 'En Ejecucion'), ('Sin Anticipo', 'Sin Anticipo'),
                          ('Terminado Anticipadamente', 'Terminado Anticipadamente'), ('Rescindido', 'Rescindido'), ('En Observacion', 'En Observacion'),
                     ('Nueva', 'Nueva'), ('Fuera de Semaforo', 'Fuera de Semaforo'), ('Falta Doc_cierre', 'Falta Doc_cierre'),
                     ('Suspendida', 'Suspendida')]

    tipo_estado_obra = fields.Selection(select_estado, string="Estado", store=True)

    estado_obra_m2o = fields.Many2one('semaforo.estado_obra_lista', string="Estado", store=True) # NUEVO ESTADO DE OBRA

    select_estado2 = [('Abierto', 'Abierto'), ('Cerrado', 'Cerrado'), ('Cancelado', 'Cancelado')]
    
    tipo_estado_actividad = fields.Selection(select_estado2, string="Estado Actividad", 
                                             store=True)

    recursos_semaforo = fields.Many2many(comodel_name="autorizacion_obra.anexo_tecnico",
                                         compute="recursos_semaforox")

    @api.one
    def recursos_semaforox(self):
        partidas = self.env['partidas.partidas']
        anexos = self.env['autorizacion_obra.anexo_tecnico'].search([("concepto.id", "=", self.obra.id)])
        for i in anexos:
            datos_anexo = {
                'recursos_semaforo': [[4, i.id, {}
                ]]
                }

            anex_est = partidas.browse(self.id)
            recursos_semaforo = anex_est.update(datos_anexo)

    convenio_semaforo = fields.Many2many(comodel_name="proceso.convenios_modificado", compute="semaforo_convenios")

    # METODO PARA INGRESAR A PROPUESTAS BOTON
    @api.multi
    def convenio_escalatoria(self):
        # VISTA OBJETIVO
        view = self.env.ref('proceso_contratacion.proceso_convenios_escalatoria')
        # BUSCAR VISTA
        return {
            'type': 'ir.actions.act_window',
            'name': 'Convenio Escalatoria',
            'res_model': 'proceso.convenios_modificado',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
        }

    tabla_pagos = fields.Many2many('control.ordenes_cambio', string='Pagos de Estimaciones', compute="tabla_pagos_estimaciones") # TABLA DE LOS PAGOS DE ESTIMACIONES RELACIONADAS

    @api.one
    def tabla_pagos_estimaciones(self):
        partidas = self.env['partidas.partidas']
        pagos = self.env['control.ordenes_cambio'].search([("numero_contrato.id", "=", self.id)])
        for i in pagos:
            datos_pagos = {
                'tabla_pagos': [[4, i.id, {}
                                       ]]
            }
            pagos_est = partidas.browse(self.id)
            tabla_pagos = pagos_est.update(datos_pagos)

    avance_semaforo = fields.Many2many(comodel_name="proceso.iavance", compute="semaforo_avance")

    porcentajeProgramado = fields.Float(string="", digits=(12, 2)) 

    atraso = fields.Float(string="", digits=(12,2)) # compute="porProgramado"

    select_color = [('Verde', 'Verde'), ('Amarillo', 'Amarillo'), ('Rojo', 'Rojo')]
    color_semaforo = fields.Selection(select_color, string="Estado de Semaforo")

    programa_semaforo = fields.Many2many(comodel_name="proceso.programa", compute="semaforo_programa")

    @api.multi
    def imprimir_accion_excel(self):
        url = "http://sidur.galartec.com:4000/finiquito/" + str(self.id)
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.one
    def semaforo_programa(self):
        # MODELO DONDE ESTA EL M2M
        partidas = self.env['partidas.partidas']

        # BUSQUEDA DE LOS DATOS 
        prog = self.env['programa.programa_obra'].search(
            [("obra.id", "=", self.id)])

        # ITERACION DE LA BUSQUEDA
        for i in prog.programa_contratos:
            # OBJETO CON LOS DATOS
            datos_p = {
                'programa_semaforo': [[4, i.id, {
                }]]}

            # BUSCAR EN QUE MODELO VAMOS A ACTUALIZAR ESOS DATOS
            partida_est = partidas.browse(self.id)
            # UPDATE PARA ACTUALIZAR LA TABLA
            programa_semaforo = partida_est.update(datos_p)

    a_fis = fields.Float(string="", store=True, digits=(12, 2) )
    a_fin = fields.Float(string="", store=True, digits=(12, 2))
    total_estimado = fields.Float(string="Total Importe liquido estimado", ) # TOTAL IMPORTE LIQUIDO
    total_estimacion = fields.Float(string="Total de conceptos estimados", compute="total_estimado_m" ) # TOTAL ESTIMADO
    total_amort_anticipo = fields.Float(string="Total de Amort Anticipo", compute="total_estimado_m" ) # TOTAL AMORT ANTICIPO
    pagado_estimacion = fields.Float(string="Total Pagado de Estimacion",) # MONTO ACUTAL PAGADO ESTIMADO
    pagado_anticipo = fields.Float(string="Total Pagado de Anticipo",) # MONTO ACUTAL PAGADO ANTICIPO
    estimado_pagado = fields.Boolean('Estimacion Totalmente Pagada', ) # INDICA SI YA SE PAGO COMPLETAMENTE
    anticipo_pagado = fields.Boolean('Anticipo Totalmente Pagado', ) # INDICA SI YA SE PAGO COMPLETAMENTE

    @api.one
    def total_estimado_m(self):
        acum = 0
        acum_amort = 0
        for i in self.esti:
            acum += i.estimado
            acum_amort += i.amort_anticipo
        self.total_estimacion = acum
        self.total_amort_anticipo = acum_amort
    

    @api.one
    def semaforo_avance(self):
        partidas = self.env['partidas.partidas']
        avanc = self.env['proceso.iavance'].search(
            [("numero_contrato.id", "=", self.id)])

        for i in avanc:
            datos_avance = {
                'avance_semaforo': [[4, i.id, {
                }]]}
            partida_est = partidas.browse(self.id)
            avance_semaforo = partida_est.update(datos_avance)
    @api.one
    @api.multi
    def semaforo_convenios(self):
        partidas = self.env['partidas.partidas']

        conv = self.env['proceso.convenios_modificado'].search(
            [("nombre_contrato", "=", self.nombre_contrato)])

        for i in conv:
            datos_conv = {
                'convenio_semaforo': [[4, i.id, {
                }]]}
            partida_est = partidas.browse(self.id)
            convenio_semaforo = partida_est.update(datos_conv)

    @api.one
    def _calc_url(self):
        original_url = "http://sidur.galartec.com:56733/galeria/?id=" + str(self.id)
        self._url = original_url

    @api.multi
    def imprimir_accion(self):
        return {"type": "ir.actions.act_url", "url": self._url, "target": "new", }

    # METODO PARA CREAR NUEVO DOCUMENTO CON BOTON
    @api.multi
    def expediente_crear(self):
        # VISTA OBJETIVO
        view = self.env.ref('control_expediente.form_agregar_control_expediente')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Control Expediente',
            'res_model': 'control.expediente',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_p_id': self.id,
                        'default_auxiliar': True, 'default_auxiliar_comprimido': True },
            'view_id': view.id,
        }

    @api.multi
    def agregar_expedientes(self):
        if self.tabla_control:
            pass
        else:
            b_contrato = self.env['proceso.elaboracion_contrato'].search([('contrato', '=', self.nombre_contrato)])[0]
            var = ''
            if b_contrato.adjudicacion: # ADJUDICACION
                if b_contrato.adjudicacion.normatividad == '1':  # 1 = federal
                    var = 'Adjudicación Federal'
                else: # estatal
                    var = 'Adjudicación Estatal'
            else: # LICITACION
                if b_contrato.obra.tipolicitacion == '1':  # 1 = LIC PUBLICA
                    if b_contrato.obra.normatividad == '1':  # FEDERAL
                        var = 'Licitación Publica Federal'
                    else: # ESTATAL
                        var = 'Licitación Publica Estatal'
                else:  # LIC SIMPLIFICADA
                    if b_contrato.obra.normatividad == '1':  # FEDERAL
                        var = 'Licitación Simplificada Estatal'
                    else: # ESTATAL
                        var = 'Licitación Simplificada Federal'

            b_expediente = self.env['control_expediente.control_expediente'].search([('tipo_expediente.tipo_expediente', '=', var)],
                                                                                    order='orden asc')
            numeracion = 0
            for vals in b_expediente:
                numeracion += 1
                datos = { 'tabla_control':
                    [[0,0,
                      {
                          'numeracion': numeracion,
                          'orden': vals.orden,
                          'nombre': vals.id,
                          'nombre_documento': vals.nombre,
                          'contrato_id': b_contrato.id,
                          'auxiliar': False,
                          'id_documento_categoria': None,
                          'auxiliar_comprimido': False,
                          'auxiliar_documentos_categoria': False,
                          'auxiliar_documentos_categoria2': False,
                          'p_id': self.id,
                          'responsable': vals.responsable.id,
                          'etapa': vals.etapa,
                          'categoria_documento': vals.categoria_documento.id,
                      }
                      ]] }
                tt = self.env['partidas.partidas'].browse(self.id)
                xd = tt.write(datos)

    # ACTIVADOR DE ONCHANGE PARA PRUEBAS
    prueba_expediente = fields.Char(string="PRUEBA METODO EJECUCION", required=False, )

    '''@api.one
    def estimaciones_report(self):
        partidas = self.env['partidas.partidas']
        dedu = self.env['control.estimaciones'].search(
            [("obra.id", "=", self.id)])
        acum = 0
        for i in dedu:
            datos_esti = {
                'esti': [[4, i.id, {
                }]]}

            partida_est = partidas.browse(self.id)
            esti = partida_est.update(datos_esti)'''

    # METODO DE CONTAR REGISTROS DE FINIQUITOS PARA ABRIR VISTA EN MODO NEW O TREE VIEW
    @api.one
    def ContarEstimaciones(self):
        count = self.env['control.estimaciones'].search_count([('obra', '=', self.id)])
        self.contar_estimaciones = count

    @api.multi
    def CategoriasForm(self):
        view = self.env.ref('proceso_contratacion.categoria_seccion_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Categorias',
            'res_model': 'catalogo.categoria',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
        }

    @api.multi
    def conceptos_estimados_tree(self):
        view = self.env.ref('ejecucion_obra.detalle_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'CONCEPTOS ESTIMADOS',
            'res_model': 'control.detalle_conceptos',
            'view_mode': 'tree',
            'limit': 500,
            'view_id': view.id,
            'domain': [('estimacion', '!=', 0)],
        }

    # METODO PARA INGRESAR A RECURSOS BOTON
    @api.multi
    def ProgramasVentana(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.vista_form_programa')
        # CONTADOR SI YA FUE CREADO
        count = self.env['programa.programa_obra'].search_count([('obra.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['programa.programa_obra'].search([('obra.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA

        b_fechas_p = self.env['programa.programa_obra'].browse(search.id)
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'current',
                'view_id': view.id,
                'res_id': search[0].id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'current',
                'view_id': view.id,
            }

    @api.multi
    def ProgramasVentanaSupervision(self):
        # VISTA OBJETIVO
        view = self.env.ref('supervision_obra.vista_form_programa_supervision')
        # CONTADOR SI YA FUE CREADO
        count = self.env['programa.programa_obra'].search_count([('obra.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['programa.programa_obra'].search([('obra.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA

        b_fechas_p = self.env['programa.programa_obra'].browse(search.id)
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search[0].id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Programa',
                'res_model': 'programa.programa_obra',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }

    @api.one
    def FechaAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.fecha_anticipos = search.fecha_anticipos

    @api.one
    def PorcentajeAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.porcentaje_anticipo = search.porcentaje_anticipo

    @api.one
    def TotalAnticipo(self):
        search = self.env['anticipo.anticipo'].search([('obra.id', '=', self.id)])
        self.total_anticipo = search.total_anticipo

    # METODO PARA ABRIR ANTICIPOS CON BOTON
    @api.multi
    def anticipoBoton(self):
        view = self.env.ref('proceso_contratacion.partidas_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'anticipos',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': self.id,
        }

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        if self.iva_frontera:
            iva = 0.08
        else:
            iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = float(iva)

    # METODO PARA VERIFICAR SI HAY PROGRAMAS
    @api.one
    def programa_verif(self):
        busqueda2 = self.env['proceso.programa'].search_count([('obra.id', '=', self.id)])
        if busqueda2 >= 1:
            self.verif_programa = True
        else:
            self.verif_programa = False

    # METODO PARA VERIFICAR SI YA SE ANTICIPO UNA PARTIDA
    @api.one
    def anticipada_Sel(self):
        if self.fecha_anticipos and self.numero_fianza and self.afianzadora and self.fecha_fianza:
            self.anticipada = True
        else:
            self.anticipada = False

    # METODO PARA VERIFICAR SI HAY ANTICIPO
    @api.multi
    def VerifAnti(self, vals):
        if self.fecha_anticipos and self.fecha_fianza and self.afianzadora and self.numero_fianza and self.anticipo_material is not False:
            self.anticipada = True
        else:
            self.anticipada = False

    # METODO PARA CALCULAR EL PORCENTAJE DEL ANTICIPO
    @api.one
    @api.depends('porcentaje_anticipo')
    def anticipo_por(self):
        for rec in self:
            rec.update({
                'total_anticipo_porcentaje': float(rec.porcentaje_anticipo)
            })

    # METODO PARA CALCULAR EL ANTICIPO DE INICIO
    @api.onchange('fecha_anticipos', 'porcentaje_anticipo', 'anticipo_material')
    def anticipo_inicio(self):
        for rec in self:
            rec.update({
                'anticipo_a': rec.monto_partida * rec.total_anticipo_porcentaje
            })

    # MEOTODO PARA CALCULAR IVA DE ANTICIPO ---VER CUESTION DEL IVA
    @api.multi
    @api.onchange('fecha_anticipos', 'porcentaje_anticipo', 'anticipo_material')
    def anticipo_iva(self):
        for rec in self:
            rec.update({
                'iva_anticipo': rec.anticipo_a * self.b_iva
            })

    # METODO PARA CALCULAR EL TOTAL DEL ANTICIPO
    @api.multi
    @api.onchange('fecha_anticipos', 'porcentaje_anticipo', 'anticipo_material')
    def anticipo_total(self):
        for rec in self:
            rec.update({
                'total_anticipo': rec.anticipo_a + rec.iva_anticipo
            })

    # METODO PARA INSERTAR EL NUMERO DEL CONTRATO DENTRO DE LA PARTIDA PARA HACER CONEXION
    '''@api.one
    def nombrePartida(self):
        self.numero_contrato = self.enlace.id'''

    # METODO DE JCHAIRZ
    
    # @api.onchange('ruta_critica')
    @api.multi
    @api.onchange('ruta_critica')
    def total_ruta_critica(self): # suma_importe
        suma = 0
        for i in self.ruta_critica:
            resultado = i.porcentaje_est
            suma += resultado
        self.total_ = suma

    # JCHAIREZ
    @api.onchange('total_')
    def validar_total_importe(self):
        if self.total_ > 100:
            raise ValidationError("Ups! el porcentaje no puede ser mayor a 100 %")

    # Jesus Fernandez metodo para abrir ruta critica
    @api.multi
    def ruta_critica_over(self):
        view = self.env.ref('supervision_obra.supervision_obra_supervision_obra_proceso_rutac_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ruta critica',
            'res_model': 'partidas.partidas',
            'view_mode': 'form',
            'target': 'current',
            'view_id': view.id,
            'res_id': self.id,
        }

    # JFernandez metodo para contar el numero de convenios que tiene cada obra
    @api.one
    def contar_covenios(self):
        count = self.env['proceso.convenios_modificado'].search_count([('nombre_contrato', '=', self.nombre_contrato)])
        self.count_convenios_modif = count

    # METODO CALCULAR DIFERENCIA ENTRE PARTIDA Y CONCEPTOS
    @api.one
    def Diferencia(self):
        _search_cove = self.env['proceso.convenios_modificado'].search_count([("nombre_contrato", "=", self.nombre_contrato),("tipo_convenio", "=", 'PL' or 'BOTH')])
        for rec in self:
            if _search_cove == 0:
                rec.update({
                    'diferencia': self.total_catalogo - self.monto_partida
                })
            else:
                rec.update({
                    'diferencia': self.total_catalogo - self.total
                })

    # METODO CALCULAR TOTAL PARTIDA UNICA
    '''@api.one
    @api.depends('monto_partida')
    def SumaContrato(self):
        for rec in self:
            rec.update({
                # 'total_partida': (rec.monto_partida * self.b_iva) + rec.monto_partida,
                'monto_sin_iva': rec.monto_partida
            })'''

    # CALCULAR EL IVA TOTAL
    '''@api.one
    @api.depends('monto_partida')
    def iva(self):
        for rec in self:
            rec.update({
                'iva_partida': (rec.monto_partida * self.b_iva)
            })'''

    # METODO PARA SUMAR LOS IMPORTES DE LOS CONCEPTOS
    @api.one
    @api.depends('conceptos_partidas')
    def SumaImporte(self):
        suma = 0
        for i in self.conceptos_partidas:
            resultado = i.importe
            suma = suma + resultado
            self.total_catalogo = suma

    # METODO DE ENLACE A ESTIMACIONES
    @api.one
    def nombre(self):
        self.estimacion_id = self.obra


class ConveniosM(models.Model):
    _name = 'proceso.convenios'

    fecha_convenios = fields.Date("Fecha:")
    referencia_convenios = fields.Char("Referencia:")
    observaciones_convenios = fields.Char("Observaciones:")
    tipo_convenio = fields.Char("Tipo de Convenio:", default="Escalatorio", readonly="True")
    importe_convenios = fields.Float('Importe:')
    iva_convenios = fields.Float('I.V.A:')
    total_convenios = fields.Float('Total:')


# CONTENIDO DE LA TABLA DE PROGRAMA DE OBRA
class ProgramaContrato(models.Model):
    _name = 'proceso.programa'

    obra = fields.Many2one('partidas.partidas', string='Partida:', store=True)
    # IMPORTACION
    id_prog = fields.Integer(string="ID PROGRAMA",)
    # TERMINA IMPORTACION

    fecha_inicio = fields.Date('Fecha Inicio:', required=True) # default=fields.Date.today(),
    fecha_termino = fields.Date('Fecha Término:', required=True )

    monto = fields.Float('Monto:', )

    @api.multi
    @api.onchange('monto')
    def actualizar_programa(self):
        acum = 0
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        for x in b_programa.programa_contratos:
            if x.fecha_inicio:
                acum += 1
        if acum == 0:
            b_programa.update({
                'ultima_fecha_inicio': self.fecha_inicio
            })
        else:
            pass

    porcentaje_programa = fields.Float(compute="calcular_porcentaje", ) # store=True

    mes_actual = fields.Boolean('Mes actual', compute="_mes_actual") # para ver si es mes actual y aplicar color
    mes_paso = fields.Boolean('Ya paso', compute="_mes_actual") # para ver si es mes actual y aplicar color
    mes_restante = fields.Boolean('Restantes', compute="_mes_actual") # para ver si es mes actual y aplicar color
    mes_ultimo = fields.Boolean('Ya acabada', compute="_mes_actual") # para ver si es mes actual y aplicar color

    @api.one
    def _mes_actual(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])

        if not self.fecha_inicio or not self.fecha_termino:
            pass
        else:

            # month_hoy = datetime.datetime.now().strftime("%y-%m")
            today = date.today()
            hoy = str(today.strftime("%Y-%m-%d"))
            hoy_f = datetime.datetime.strptime(str(hoy), "%Y-%m-%d")
            hoy_ff = str(hoy_f.year) + '0' + str(hoy_f.month)

            datee = datetime.datetime.strptime(str(self.fecha_inicio), "%Y-%m-%d")
            datee2 = datetime.datetime.strptime(str(self.fecha_termino), "%Y-%m-%d")
            ff = str(datee.year) + '0' + str(datee.month)
            ff2 = str(datee2.year) + '0' + str(datee2.month)
            if str(hoy_ff) == str(ff):
                self.mes_actual = True
            else:
                pass

            if int(hoy_ff) > int(ff2):
                self.mes_paso = True
            else:
                pass

            if int(hoy_ff) < int(ff2):
                self.mes_restante = True
            else:
                pass

            if b_programa.fecha_termino_convenida is True:
                if str(hoy) > str(b_programa.fecha_termino_programa):
                    self.mes_ultimo = True
            else:
                if str(hoy) > str(b_programa.fecha_termino_programa):
                    self.mes_ultimo = True

    # @api.depends('fecha_termino')
    @api.one
    def calcular_porcentaje(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        acum = 0
        if not b_programa.total_programa:
            pass
        else:
            for i in b_programa.programa_contratos:
                if not i.fecha_termino or not self.fecha_termino:
                    pass
                else:
                    if i.fecha_termino > self.fecha_termino:
                        pass
                    elif i.fecha_termino <= self.fecha_termino:
                        acum += i.monto
                        if acum == 0 or b_programa.total_programa == 0:
                            self.porcentaje_programa = 0
                        else:
                            self.porcentaje_programa = (acum / b_programa.total_programa) * 100

    # METODO para verificar fechas de programa
    @api.multi
    @api.onchange('fecha_termino')
    def validar_fecha_programa(self):
        if str(self.fecha_termino) < str(self.fecha_inicio):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la fecha de inicio, '
                                     'por favor seleccione una fecha posterior')
        else:
            return False


    @api.model
    def create(self, values):
        res = super(ProgramaContrato, self).create(values)
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', res.obra.id)])
        b_partida = self.env['partidas.partidas'].browse(res.obra.id)
        date_format = "%Y/%m/%d"
        date_format2 = "%Y-%m-%d"
        fechainicioprog = ''
        fechaterminoprog = ''
        today = date.today()
        hoy = str(today.strftime(date_format))
        ciclo = 0
        for i in b_programa.programa_contratos:
            ciclo += 1
            if ciclo == 1:
                fechainicioprog = datetime.datetime.strptime(str(i.fecha_inicio), date_format2)
                fechaterminoprog = datetime.datetime.strptime(str(values['fecha_termino']), date_format2)

            else:
                fechaterminoprog = datetime.datetime.strptime(str(values['fecha_termino']), date_format2)
        if ciclo == 0:
            fechainicioprog = datetime.datetime.strptime(str(values['fecha_inicio']), date_format2)
            fechaterminoprog = datetime.datetime.strptime(str(values['fecha_termino']), date_format2)
        _fecha_actual = datetime.datetime.strptime(str(hoy), date_format)
        r = _fecha_actual - fechainicioprog
        dias_trans = r.days + 1

        r = fechaterminoprog - fechainicioprog
        dias_totales = r.days + 1
        porcentajeProgramado = 0
        if dias_trans > dias_totales:
            porcentajeProgramado = 100
        else:
            porcentajeProgramado = dias_trans / dias_totales * 100

        atraso = porcentajeProgramado - b_partida.a_fis
        color = ''
        if atraso <= 5:
            color = 'Verde'
        elif atraso > 5 and atraso <= 25:
            color = 'Amarillo'
        elif atraso > 25:
            color = 'Rojo'

        b_partida.write({'porcentajeProgramado': porcentajeProgramado,
                         'atraso': atraso, 'color_semaforo': color,
                         })
        return res

    @api.multi
    def borrar(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        b_partida = self.env['partidas.partidas'].browse(self.obra.id)
        date_format = "%Y/%m/%d"
        date_format2 = "%Y-%m-%d"
        fechainicioprog = ''
        fechaterminoprog = ''
        today = date.today()
        hoy = str(today.strftime(date_format))
        ciclo = 0
        for i in b_programa.programa_contratos:
            ciclo += 1
            if ciclo == 1:
                fechainicioprog = datetime.datetime.strptime(str(i.fecha_inicio), date_format2)
                fechaterminoprog = datetime.datetime.strptime(str(i.fecha_termino), date_format2)
            elif i.fecha_inicio != self.fecha_inicio and i.fecha_termino != self.fecha_termino:
                fechaterminoprog = datetime.datetime.strptime(str(i.fecha_termino), date_format2)
            elif i.fecha_inicio == self.fecha_inicio and i.fecha_termino == self.fecha_termino:
                break

        _fecha_actual = datetime.datetime.strptime(str(hoy), date_format)
        r = _fecha_actual - fechainicioprog
        dias_trans = r.days + 1

        r = fechaterminoprog - fechainicioprog
        dias_totales = r.days + 1
        porcentajeProgramado = 0
        if dias_trans > dias_totales:
            porcentajeProgramado = 100
        else:
            porcentajeProgramado = dias_trans / dias_totales * 100

        atraso = porcentajeProgramado - b_partida.a_fis
        color = ''
        if atraso <= 5:
            color = 'Verde'
        elif atraso > 5 and atraso <= 25:
            color = 'Amarillo'
        elif atraso > 25:
            color = 'Rojo'

        b_partida.write({'porcentajeProgramado': porcentajeProgramado,
                         'atraso': atraso, 'color_semaforo': color,
                         })
        self.env['proceso.programa'].search([('id', '=', self.id)]).unlink()