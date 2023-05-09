from odoo import models, fields, api, exceptions
from datetime import date
from datetime import datetime
import calendar
import warnings

'''CONTROL DE ESTIMACIONES SE ENCUENTRA EN EL MODULO DE CONTRATOS PARA HACER POSIBLE UN M2M HACIA ESTIMACIONES Y PODER
SACAR UN REPORTE'''


class EstimacionMultipleEscalatoria(models.Model):
    _name = 'control.estimacion_escalatoria'

    obra = fields.Many2one('partidas.partidas', string='Obra:', readonly=True, store=True)
    idobra = fields.Char(string="Numero de Estimacion:", store=True)
    estimacion = fields.Many2one(comodel_name="control.estimaciones", string="Estimacion a Escalar", required=True, digits=(12, 2) )
    sub_total_esc = fields.Float('Subtotal de escalatoria Padre', related="estimacion.estimacion_subtotal", digits=(12, 2))
    estimado_related = fields.Float('Estimado', store=True, digits=(12, 2))
    sub_total_esc_h = fields.Float('Subtotal Escalatoria', store=True, digits=(12, 2))
    por_escalatoria = fields.Float('Ingresar el % de escalatoria')

    fecha_inicio_estimacion = fields.Date(string="Del:", store=True)
    fecha_termino_estimacion = fields.Date(string="Al:", store=True)

    @api.multi
    @api.onchange('por_escalatoria')
    def subtotal_escalatoria(self):
        self.estimado_related = self.estimacion.estimado * (1 - self.estimacion.amort_anticipo_partida)
        self.sub_total_esc_h = (self.por_escalatoria / 100) * self.estimado_related # (self.estimado_related * (1 - self.estimacion.amort_anticipo_partida))

    @api.multi
    @api.onchange('estimacion')
    def estimacion_escalatoria_num(self):
        self.idobra = self.estimacion.idobra
        self.fecha_inicio_estimacion = self.estimacion.fecha_inicio_estimacion
        self.fecha_termino_estimacion = self.estimacion.fecha_termino_estimacion
        # self.obra = self.estimacion.obra


class Estimaciones(models.Model):
    _name = 'control.estimaciones'
    _rec_name = 'clave_estimacion'

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="obra.obra.obra_planeada.ejercicio")
    observaciones_ = fields.Text('OBSERVACIONES')

    id_sideop = fields.Integer('ID SIDEOP')
    num_contrato = fields.Char('ID contrato SIDEOP')

    # NUMERO DE ESTIMACION
    idobra = fields.Char(string="Numero de Estimacion:", store=True)

    @api.multi
    @api.onchange('multiples_escalatorias')
    def est_multiple_importe(self):
        acum = 0
        for i in self.multiples_escalatorias:
            acum += i.sub_total_esc_h
        self.sub_total_esc_h = acum
        self.estimado = acum

        # SACAR VALOR DEDUCCIONES
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })
        # SUMA DE DEDUCCIONES
        sumax = 0
        for i in self.deducciones:
            resultado = i.valor
            sumax = sumax + resultado
            self.estimado_deducciones = sumax

        self.estimacion_subtotal = acum
        self.estimacion_iva = acum * self.b_iva
        self.estimacion_facturado = self.estimacion_iva + acum
        self.a_pagar = (self.estimacion_iva + acum) - self.estimado_deducciones

    # ID ESTIMACION
    ide_estimacion = fields.Char(string="ID", ) # compute="estid"
    # VER SI UTILIZAR
    estimacion_id = fields.Char()

    obra = fields.Many2one('partidas.partidas', string='Obra:', readonly=True)
    obra_id = fields.Char(compute="obra_enlace", store=True)

    clave_obra = fields.Char(string='Clave de Obra')

    autorizacion_recurso = fields.Char(string='Autorizacion de Recurso', store=True) # CAMPOS PARA REPORTE DE TRAMITE DE AUTORIZACION DE PAGO
    area_funcional = fields.Char(string='Area Funcional', store=True) # CAMPOS PARA REPORTE DE TRAMITE DE AUTORIZACION DE PAGO
    pospre = fields.Char(string='Pospre', store=True) # CAMPOS PARA REPORTE DE TRAMITE DE AUTORIZACION DE PAGO
    fondo = fields.Char(string='Fondo', store=True) # CAMPOS PARA REPORTE DE TRAMITE DE AUTORIZACION DE PAGO
    clave_estimacion = fields.Char(string='PEP', store=True)

    auxiliar_alerta_programa = fields.Boolean(string="Indica si el programa de obra esta correcto para poder proseguir con la estimacion", store=True  )
    auxiliar_alerta_fecha = fields.Boolean(string="Indica si la fecha de estimacion no es mayor a 31 dias para poder proseguir con la estimacion", store=True  )

    @api.multi
    @api.onchange('tipo_estimacion', 'fecha_inicio_estimacion', 'fecha_termino_estimacion', 'multiples_escalatorias', 'estimacion_esc')
    def clave_obra_m(self):
        date_format = "%Y-%m-%d"
        if not self.tipo_estimacion:
            pass
        else:
            self.clave_obra = self.obra.obra.obra_planeada.numero_obra
            
            search_oficio = self.env['autorizacion_obra.anexo_tecnico'].search(
                [('concepto.id', '=', self.obra.obra.id)])
            if not search_oficio:
                pass
            else:
                for so in search_oficio:
                    clave_string = so.clave_presupuestal.partition('-')
                    clave_string2 = clave_string[2].partition('-')
                    clave_string3 = clave_string2[2].partition('-')
                    clave_string4 = clave_string3[2].partition('-')
                    self.area_funcional = clave_string2[0]
                    self.pospre = clave_string3[0]
                    self.fondo = clave_string4[0]

            # self.clave_estimacion = '%s - %s' % (str(self.clave_obra), str(self.ide_estimacion),)
            num_est = self.env['control.estimaciones'].search_count([('obra', '=', self.obra.id)])
            if self.tipo_estimacion == '1': # ESTIMACION
                if not self.idobra:
                    self.clave_estimacion = 'Est. ' + str(num_est + 1)
                else:
                    self.clave_estimacion = 'Est. ' + str(self.idobra)

            if self.tipo_estimacion == '2': # ESCALATORIA
                self.clave_estimacion = 'Escalatoria Est. ' + str(self.estimacion_esc.idobra)

            if self.tipo_estimacion == '3': # ESCALATORIA
                c_m = 0
                num_est_multi = ""
                num_est_multi2 = ""
                for i in self.multiples_escalatorias:
                    c_m += 1
                    if c_m == 1:
                        num_est_multi = str(i.idobra)
                    else:
                        num_est_multi2 += str(', ' + str(i.idobra))
                self.clave_estimacion = 'Escalatoria Multiple Est. ' + str(num_est_multi) + str(num_est_multi2)

            if self.tipo_estimacion == '4':  # BIS
                self.clave_estimacion = 'Bis Est. ' + str(self.estimacion_bis.idobra)

            b_prog = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
            if b_prog.restante_programa != 0: # SI ES DIFERENTE A 0 EL PROGRAMA NO ESTA CORRECTO
                self.auxiliar_alerta_programa = True
            else:
                self.auxiliar_alerta_programa = False

            if not self.fecha_inicio_estimacion or not self.fecha_termino_estimacion:
                pass
            else:
                fie = datetime.strptime(str(self.fecha_inicio_estimacion.replace(day=1)), date_format)
                # fecha termino programa
                fte = datetime.strptime(str(self.fecha_termino_estimacion), date_format)
                dias = fte - fie
                diass = dias.days + 1
                fecha_termino_programa = ''
                for i in b_prog.programa_contratos:
                    fecha_termino_programa = i.fecha_termino
                f_sansion_est = datetime(self.fecha_termino_estimacion.year, self.fecha_termino_estimacion.month,
                                         self.fecha_termino_estimacion.day)
                f_sansion_prog = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                          fecha_termino_programa.day)
                if f_sansion_est > f_sansion_prog:
                    pass
                else:
                    if diass > 31:
                        self.auxiliar_alerta_fecha = True
                    else:
                        self.auxiliar_alerta_fecha = False

    @api.multi
    @api.onchange('estimacion_esc')
    def estimacion_escalatoria_num(self):
        self.idobra = self.estimacion_esc.idobra

    @api.one
    def pep(self):
        if self.clave_obra:
            self.clave_estimacion = '%s - %s' % (str(self.clave_obra), str(self.ide_estimacion),)
        else:
            self.clave_estimacion = self.ide_estimacion
    # ver si utilizar
    p_id = fields.Integer("ID PARTIDA", related="obra.p_id")

    # AUXILIAR DE CONEXION HACIA CONTRATO
    numero_contrato = fields.Many2one(string="nc", related="obra.numero_contrato")
    descripcion_contrato = fields.Text(related="numero_contrato.name")
    nombre_partida = fields.Many2one(related="obra.obra")

    # ESTIMACIONES
    radio_estimacion = [(
        '1', "Estimacion"), ('2', "Escalatoria"), ('3', "Escalatoria Multiple"), ('4', "Estimacion Bis")]
    tipo_estimacion = fields.Selection(radio_estimacion, string="", required=True)

    # estimacions_id = fields.Char(compute="estimacionId", store=True)
    numero_estimacion = fields.Char(string="Número de Estimación:")
    # ESTIMACIONES ESCALATORIAS
    estimacion_esc = fields.Many2one('control.estimaciones', string="Selecciona la estimacion a escalar")
    sub_total_esc = fields.Float('Subtotal de escalatoria Padre', related="estimacion_esc.estimacion_subtotal")
    sub_total_esc_h = fields.Float('Subtotal Escalatoria', store=True)

    por_escalatoria = fields.Float('Ingresar el % de escalatoria')

    multiples_escalatorias = fields.Many2many('control.estimacion_escalatoria', string='Escalatoria Multiple')

    # METODO PARA CALCULAR SUBTOTAL DE LA ESCALATORIA
    @api.multi
    @api.onchange('por_escalatoria')
    def subtotal_escalatoria(self):
        if self.tipo_estimacion == "2":
            self.sub_total_esc_h = (self.por_escalatoria / 100) * self.sub_total_esc
            self.estimado = self.sub_total_esc_h

            # SACAR VALOR DEDUCCIONES
            for rec in self.deducciones:
                rec.update({
                    'valor': self.estimado * rec.porcentaje / 100
                })
            # SUMA DE DEDUCCIONES
            sumax = 0
            for i in self.deducciones:
                resultado = i.valor
                sumax = sumax + resultado
                self.estimado_deducciones = sumax

            self.estimacion_subtotal = self.sub_total_esc_h
            self.estimacion_iva = self.sub_total_esc_h * self.b_iva
            self.estimacion_facturado = self.estimacion_iva + self.sub_total_esc_h
            self.a_pagar = (self.estimacion_iva + self.sub_total_esc_h) - self.estimado_deducciones

    fecha_inicio_estimacion = fields.Date(string="Del:", default=fields.Date.today(), required=True, store=True)
    fecha_termino_estimacion = fields.Date(string="Al:", default=fields.Date.today(), required=True, store=True)

    @api.multi
    @api.onchange('p_id')
    def fechaAnterior(self):
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        c_est = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        if c_est == 0:
            pass
        else:
            self.fecha_inicio_estimacion = b_est[int(c_est)-1].fecha_termino_estimacion
            self.fecha_termino_estimacion = b_est[int(c_est)-1].fecha_termino_estimacion

    a_fin = fields.Float(string="Avance Financiero", store=True)

    '''@api.one
    def avanceFinanciero(self):
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        acum = 0
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        for x in b_est:
            if int(self.idobra) < int(x.idobra):
                pass
            else:
                acum += x.estimado
                self.a_fin = (acum / b_programa.total_programa) * 100'''

    fecha_presentacion = fields.Date(string="Fecha de presentación:")
    fecha_revision = fields.Date(string="Fecha revisión Residente:")

    notas = fields.Text(string="Notas:", required=False, )

    # DEDUCCIONES
    deducciones = fields.Many2many('control.deducciones', string="Deducciones:", store=True)

    # CALCULO DE LA ESTIMACION
    estimado = fields.Float(string="Importe ejecutado estimación:", store=True, digits=(12,2)) # compute="suma_conceptos", store=True
    amort_anticipo = fields.Float(string="Amortización de Anticipo:", store=True, digits=(12,2)) #  compute="amortizacion_anticipo",

    # amort_anticipo_partida = fields.Float(related="obra.numero_contrato.contrato_partida_adjudicacion.porcentaje_anticipo")
    # % anticipo de amort. estimacion
    amort_anticipo_partida = fields.Float(store=True)

    @api.multi
    @api.onchange('p_id')
    def b_anticipos(self):
        b_contrato = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])
        self.amort_anticipo_partida = float(b_contrato.porcentaje_anticipo) + float(b_contrato.anticipo_material)

    estimacion_subtotal = fields.Float(string="Neto Estimación sin IVA:",  store=True, digits=(12,2)) # compute="Estimacion_sinIva",
    estimacion_iva = fields.Float(string="I.V.A. 16%", store=True, digits=(12,2)) # compute="Estimacion_Iva",
    estimacion_facturado = fields.Float(string="Neto Estimación con IVA:", store=True, digits=(12,2))

    estimado_deducciones = fields.Float(string="Menos Suma Deducciones:", store=True, digits=(12,2)) # compute="SumaDeducciones",

    # ret_dev = fields.Float(string="Retención/Devolución:", required=False, )

    sancion = fields.Float(string="Sanción por Incump. de plazo:", digits=(12,2)) # compute="_sancion",

    '''@api.multi
    @api.onchange('conceptos_partidas')
    def _sancion(self):
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        acumsancion = 0
        for p in b_est:
            acumsancion += p.ret_neta_est
        self.sancion = acumsancion'''

    a_pagar = fields.Float(string="Importe liquido:", store=True, digits=(12,2) ) # store=True compute="Importe_liquido",

    # PENAS CONVENCIONALES
    menos_clau_retraso = fields.Float(string="Menos Clausula Retraso:", required=False, )
    sancion_incump_plazo = fields.Integer(string="Sanción por Incump. de plazo:", required=False, )

    # CONCEPTOS EJECUTADOS
    conceptos_partidas = fields.Many2many('control.detalle_conceptos', store=True)  # compute="conceptosEjecutados"

    total_conceptos = fields.Float(string="Total:", required=False, digits=(12,2))

    # ID DE LA ESTIMACION
    estimacion_ids = fields.Char(string="ID")

    # IVA
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", store=True) # compute="BuscarIva",

    # DATOS DEL CONTRATO PARA REPORTE
    fecha_contrato = fields.Date(string="", related="obra.fecha", )

    # monto_contrato = fields.Float(string="", related="obra.total_partida", )
    monto_contrato = fields.Float(string="", compute="b_monto_contrato", digits=(12,2))

    @api.one
    def b_monto_contrato(self):
        search = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])
        _search_cove = self.env['proceso.convenios_modificado'].search_count([("nombre_contrato", "=", self.obra.nombre_contrato)])
        if _search_cove >= 1:
            self.monto_contrato = search.total
        elif _search_cove == 0:
            self.monto_contrato = search.monto_partida

    tabla_convenios = fields.Many2many('proceso.convenios_modificado', string='Tabla convenios para Reporte', compute="convenios_tabla")

    @api.one
    def convenios_tabla(self):
        _search_cove = self.env['proceso.convenios_modificado'].search([("contrato.id", "=", self.obra.id)],
                                                                       order='fecha_convenios desc')
        estimacion = self.env['control.estimaciones']
        acum = 0
        for i in _search_cove:
            if i.tipo_convenio == 'PL' or i.tipo_convenio == 'MT' or i.tipo_convenio == 'BOTH':
                acum += 1
                if acum == 4:
                    break
                else:
                    datos_convenio = {
                        'tabla_convenios': [[4, i.id, {}]]
                    }
                    estimacion_ = estimacion.browse(self.id)
                    tabla_convenios = estimacion_.update(datos_convenio)

    anticipo_contrato = fields.Float(string="", related="obra.anticipo_a", digits=(12,2) )
    fechainicio_contrato = fields.Date(string="", related="obra.fechainicio", )
    fechatermino_contrato = fields.Date(string="", related="obra.fechatermino", )
    municipio_contrato = fields.Many2one(string="", related="obra.municipio", )
    tipobra_contrato = fields.Many2one(string="", related="obra.obra.obra_planeada.tipoObra", )
    contratista_contrato = fields.Many2one(string="", related="obra.contratista", )
    programa = fields.Many2one(string="", related="obra.programaInversion", )
    subdirector_contrato = fields.Char(string="", compute="BuscarDirector")

    # DATOS Y CAMPOS CALCULADOS PARA REPORTE DE RETENCION
    fecha_inicio_programa = fields.Date(compute="B_fechas_programa") # compute="B_fechas_programa",
    fecha_termino_programa = fields.Date(compute="B_fechas_programa") # compute="B_fechas_programa",

    # DIAS TRANSCURRIDOS DEL INICIO DEL PROGRAMA HASTA EL TERMINO EST ACTUAL
    dias_transcurridos = fields.Integer(store=True)

    # reduccion = fields.Float(compute="MontoProgramadoESt", string='Reduccion')

    # RETENIDO ANTERIORMENTE
    retenido_anteriormente = fields.Float(string='', store=True, digits=(12,2)) #  compute="retAnt",

    '''@api.multi
    @api.onchange('conceptos_partidas')
    def retAnt(self):
        b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        if int(b_est_count) == 0 or int(self.idobra) == 1:
            self.retenido_anteriormente = 0
        else:
            if self.idobra:
                if b_est[int(self.idobra) - 2].total_ret_est > 0:
                    ret_ant = b_est[int(self.idobra) - 2].total_ret_est
                    self.retenido_anteriormente = float(ret_ant)
                else:
                    ret_ant = b_est[int(self.idobra) - 2].total_ret_est * (-1)
                    self.retenido_anteriormente = float(ret_ant)
            else:
                if b_est[int(b_est_count) - 1].total_ret_est > 0:
                    ret_ant = b_est[int(b_est_count) - 1].total_ret_est
                    self.retenido_anteriormente = float(ret_ant)
                else:
                    ret_ant = b_est[int(b_est_count) - 1].total_ret_est * (-1)
                    self.retenido_anteriormente = float(ret_ant)'''


    # MONTO EJECUTADO REAL PARA ESTA ESTIMACION
    montoreal = fields.Float(store=True, string='MONTO EJECUTADO REAL PARA ESTA ESTIMACION', digits=(12,2)) # compute="MontoRealEst"

    devolucion_est = fields.Float(string='', store=True, digits=(12, 2))  # compute='devolucion_est_metod',

    # MONTO PROGRAMADO PARA ESTA ESTIMACION
    monto_programado_est = fields.Float(digits=(12, 2), store=True)  # compute="PenasConvencionales",
    diasdif = fields.Integer(string='Dias de diferencia',store=True ) #  compute="PenasConvencionales",
    dias_desfasamiento = fields.Float(string='DIAS DE DESFASAMIENTO',  store=True ) # compute="PenasConvencionales",
    monto_atraso = fields.Float(string='MONTO DE ATRASO', digits=(12, 2), store=True) # compute="PenasConvencionales",
    diasperiodo = fields.Float(string='Dia total del periodo', store=True ) # compute="PenasConvencionales",
    diasest = fields.Float(string='',store=True ) #  compute="PenasConvencionales",
    diastransest = fields.Float(string='', store=True ) # compute="PenasConvencionales",
    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
    total_ret_est = fields.Float(string='', digits=(12, 2), store=True ) # compute="PenasConvencionales",
    porcentaje_est = fields.Float(string='', store=True ) # compute="PenasConvencionales",
    # PORCENTAJE DE LA RETENCION TOTAL
    porc_total_ret = fields.Float(string='',  store=True) # compute="PenasConvencionales",
    # RETENCION NETA A APLICAR EN ESTA ESTIMACION
    ret_neta_est = fields.Float(string='', store=True, digits=(12,2)) # compute="PenasConvencionales",
    # DEVOLUCION A EFECTUAR EN ESTA ESTIMACION
    # MONTO DIARIO PROGRAMADO
    montodiario_programado = fields.Float(string='MONTO DIARIO PROGRAMADO', digits=(12, 2), store=True) #  compute="PenasConvencionales",
    # DIAS EJECUTADOS REALCES CON RELACION  AL MONTO DIARIO PROGRAMADO
    diasrealesrelacion = fields.Float(string='DIAS EJECUTADOS REALCES CON RELACION AL MONTO DIARIO PROGRAMADO',
                                      digits=(12, 2)
                                      , store=True) # compute="PenasConvencionales",

    # CAMPOS RELACIONADOS DESDE CONTRATO PARA LA RETENCION
    select = [('diario', 'Diario'), ('mensual', 'Mensual'), ('ninguno', 'Ninguno')]
    periodicidadretencion = fields.Selection(select, string="Periodicidad Retención",
                                             related="obra.numero_contrato.periodicidadretencion")
    retencion = fields.Float(string="% Retención", related="obra.numero_contrato.retencion")
    porcentaje_sancion = fields.Float(string="% Sancion", related="obra.numero_contrato.sancion", digits=(12, 3))

    # EXCEL
    _url = fields.Char(compute="_calc_url", string="Vista de impresión")
    # PRUEBA
    ultimomonto = fields.Float(store=True)

    # xd = fields.Float(compute="computeSeccion")

    # ESTADO DE CUENTA PARA QWEB
    acum_anterior = fields.Float(compute="estado_cuenta")
    acum_total = fields.Float(compute="estado_cuenta")
    saldo_contrato = fields.Float(compute="estado_cuenta")

    acum_anterior_anti = fields.Float(compute="estado_cuenta")
    acum_total_anti = fields.Float(compute="estado_cuenta")
    saldo_contrato_anti = fields.Float(compute="estado_cuenta")

    radio_aplica = [('1', "Estimación Finiquito"), ('2', "Amortizar Total Anticipo"), ('3', "Ninguno")]
    radio_aplica2 = [('1', "Estimación Finiquito"), ('2', "Ninguno")]
    si_aplica = fields.Selection(radio_aplica, string="")
    si_aplica2 = fields.Selection(radio_aplica2, string="")

    si_aplica_estimacion = fields.Boolean('Estimación Finiquito')
    si_aplica_amortizar = fields.Boolean('Amortizar Total Anticipo')

    '''@api.onchange('si_aplica')
    def estimacion_finiquito(self):
        if self.si_aplica == '1':
            search = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
            acum = 0
            ret = self.ret_neta_est
            for i in search:
                acum += i.ret_neta_est
            self.ret_neta_est = (acum * -1) - (ret * -1)
            self.devolucion_est = (acum * -1) - (ret * -1)
        else:
            pass'''

    @api.one
    def estado_cuenta(self):
        search = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        search_c = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        acum = 0
        acum_anti = 0
        for i in search:
            if not self.idobra:
                if int(search_c+1) < int(i.idobra):
                    pass
                elif int(search_c+1) > int(i.idobra):
                    acum += i.estimado
                    acum_anti += i.amort_anticipo

                self.acum_anterior = acum
                self.acum_total = acum + self.estimado
                self.saldo_contrato = self.monto_contrato - self.acum_total

                self.acum_anterior_anti = acum_anti
                self.acum_total_anti = acum_anti + self.amort_anticipo
                self.saldo_contrato_anti = self.obra.anticipo_a - self.acum_total_anti
            else:
                if int(self.idobra) < int(i.idobra):
                    pass
                elif int(self.idobra) > int(i.idobra):
                    acum += i.estimado
                    acum_anti += i.amort_anticipo
                self.acum_anterior = acum
                self.acum_total = acum + self.estimado
                self.saldo_contrato = self.monto_contrato - self.acum_total

                self.acum_anterior_anti = acum_anti
                self.acum_total_anti = acum_anti + self.amort_anticipo
                self.saldo_contrato_anti = self.obra.anticipo_a - self.acum_total_anti

    con_orden = fields.Boolean(string="Orden Pago", readonly=True)

    '''@api.one
    def _con_orden(self):
        count = self.env['control.ordenes_cambio'].search_count([('vinculo_estimaciones.id', '=', self.id)])
        if count == 1:
            self.con_orden = True
        else:
            self.con_orden = False'''

    @api.multi
    def OrdenesPago(self):
        # VISTA OBJETIVO
        view = self.env.ref('Finanzas.orden_cambio_form')
        tree = self.env.ref('Finanzas.ordenes_tree')
        # CONTADOR SI YA FUE CREADO
        count = self.env['control.ordenes_cambio'].search_count([('vinculo_estimaciones.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['control.ordenes_cambio'].search([('vinculo_estimaciones.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count >= 1: # TIENE 2 ORDENES DE PAGO
            return {
                'type': 'ir.actions.act_window',
                'name': 'Ordenes de Pago',
                'res_model': 'control.ordenes_cambio',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'target': 'new',
                'domain': [('vinculo_estimaciones', '=', self.id)],
                # 'view_id': view.id,
                'context': {'default_vinculo_estimaciones': self.id, 'default_numero_contrato': self.obra.id,
                            'default_monto_total': self.a_pagar,
                            'default_clave_obra': self.clave_obra, 'default_tipo_pago': 'Estimacion'},
                'views': [
                    (tree.id, 'tree'),
                    (view.id, 'form'),
                ],
                # 'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Ordenes de Pago',
                'res_model': 'control.ordenes_cambio',
                'view_mode': 'form',
                'context': {'default_vinculo_estimaciones': self.id, 'default_numero_contrato': self.obra.id, 'default_monto_total': self.a_pagar,
                             'default_clave_obra': self.clave_obra, 'default_tipo_pago': 'Estimacion'},
                'target': 'new',
                'view_id': view.id,
            }

    @api.multi
    def imprimir_accion_excel(self):
        url = "/finiquito_excel_conceptos/finiquito_excel_conceptos/?id=" + str(self.id)
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    # METODO DE PRUEBA PARA UN REPORTE
    @api.multi
    def computeSeccion(self):
        for i in self.conceptos_partidas:
            if i.categoria.name is i.categoria.parent_id.name:
                self.xd = 1
            else:
                self.xd = 1
        self.xd = 1

    # TOTAL DE CONCEPTOS EJECUTADOS EXCEL
    @api.one
    def _calc_url(self):
        original_url = "/registro_obras/registro_obras/?id="
        self._url = original_url + str(self.id)

    @api.multi
    def imprimir_accion(self):
        return {
            "type": "ir.actions.act_url",
            "url": self._url,
            "target": "new",
        }

    nuevo_metodo = fields.Boolean(string="si fue activado penas convencionales mostrar otro qweb",  )

    dias_atraso_sancion = fields.Integer(string="Dias de Atraso de la Sancion", required=False, store=True)          

    @api.one
    def B_fechas_programa(self):
        date_format = "%Y-%m-%d"
        b_fecha = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        if not b_fecha.fecha_inicio_programa:
            pass
        else:
            # _search_cove = self.env['proceso.convenios_modificado'].search_count([("contrato_contrato", "=", self.obra.numero_contrato.id), '|' , ("tipo_convenio", "=", 'BOTH'),("tipo_convenio", "=", 'PL')])
            # b_convenio = self.env['proceso.convenios_modificado'].search([('contrato_contrato', '=', self.obra.numero_contrato.id)])
            fecha_prog = ""
            fecha_prog2 = ""
            for i in b_fecha.programa_contratos:
                fecha_prog = datetime.strptime(str(i.fecha_inicio), date_format).date()
                fecha_prog2 = datetime.strptime(str(i.fecha_termino), date_format).date()

            self.fecha_inicio_programa = fecha_prog
            self.fecha_termino_programa = fecha_prog2
                

    # METODO BUSCAR DIRECTOR DE OBRAS CONFIGURACION
    @api.one
    def BuscarDirector(self):
        b_director = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_subdirector_obra')
        self.subdirector_contrato = b_director

    # ID DE LA ESTIMACION
    '''@api.one
    def estid(self):
        numero = 100000 + self.id
        self.ide_estimacion = str(numero)'''

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.multi
    @api.onchange('conceptos_partidas')
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # NUMERO ESTIMACION
    @api.model
    def create(self, values):
        res = super(Estimaciones, self).create(values)
        search = self.env['partidas.partidas'].search([('id', '=', int(res.obra.id))])
        partida = self.env['partidas.partidas'].browse(search.id)
        data = {'a_fin': res.a_fin}
        xd = partida.write(data)
        datos_esti = {
            'esti': [[4, res.id, {
            }]]}
        r = partida.update(datos_esti)
        if values['estimacion_bis']:
            estimacion_bis = self.env['control.estimaciones'].browse(values['estimacion_bis'])
            for value in estimacion_bis:
                for dec in value['deducciones']:
                    dec.write({
                        'valor': (value['estimado'] - values['estimado']) * dec.porcentaje / 100
                    })
                suma2 = 0
                for i in value['deducciones']:
                    resultado = i.valor
                    suma2 = suma2 + resultado

                estimado = value['estimado'] - values['estimado']
                estimacion_subtotal = (value['estimado'] - values['estimado']) - value['amort_anticipo']
                estimacion_iva = estimacion_subtotal * values['b_iva']
                estimacion_facturado = estimacion_subtotal + estimacion_iva  # (((rec.estimado - self.estimado) - rec.amort_anticipo) * self.b_iva) + (rec.estimado - self.estimado)
                value.write({
                    'estimado': estimado,
                    'estimacion_subtotal': estimacion_subtotal,
                    'estimacion_iva': estimacion_iva,
                    'estimacion_facturado': estimacion_facturado,
                    'estimado_deducciones': suma2,
                })

                if value['sancion'] > 0:
                    value.write({
                        # SE SANCION
                        'a_pagar': (estimacion_facturado - suma2) - value['sancion'] + value['devolucion_est'] - (
                                    value['ret_neta_est'] * -1)
                    })
                elif value['retenido_anteriormente'] <= value['total_ret_est']:
                    value.write({
                        # SE RETIENE
                        'a_pagar': (estimacion_facturado - suma2) - (value['ret_neta_est'] * -1)
                    })

                elif value['retenido_anteriormente'] > value['total_ret_est']:
                    # SE DEVUELVE
                    value.write({
                        'a_pagar': (estimacion_facturado - suma2) + value['devolucion_est']
                    })
        numero = 100000 + res.id
        estimacion_id = self.env['control.estimaciones'].browse(res.id)
        num_est = self.env['control.estimaciones'].search_count([('obra', '=', res.obra.id)])
        estimacion_id.write({
            'ide_estimacion': str(numero),
            'idobra': num_est
        })
        return res

    # METODO CREATE PARA CREAR LA ID DE ESTIMACION
    @api.multi
    @api.onchange('obra')
    def IdEstimacion(self):
        self.estimacion_ids = str(self.env['control.estimaciones'].search_count([('obra', '=', self.obra.id)]))

    # METODO PARA JALAR DATOS DE LAS DEDUCCIONES DEL CONTRATO

    @api.multi  # if these fields are changed, call method
    @api.onchange('p_id')
    def deduccion(self):
        b_deducciones = self.env['proceso.elaboracion_contrato'].browse(self.numero_contrato.id)
        self.update({
            'deducciones': [[5]]
        })

        for deducciones in b_deducciones.deducciones:
            self.update({
                'deducciones': [[0, 0, {'name': deducciones.name,
                                        'porcentaje': deducciones.porcentaje}]]
            })

    # METODO PARA INSERTAR CONCEPTOS CONTRATADOS
    @api.multi
    @api.onchange('p_id')
    def conceptosEjecutados(self):
        adirecta_id = self.env['partidas.partidas'].browse(self.obra.id)
        # BUSCAR ESTIMADO ANTERIOR
        # b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        c_est = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        
        

        if int(c_est) == 0:
            b_concepto_original = self.env['proceso.conceptos_part'].search([('id_partida.id', '=', self.obra.id)])
            for conceptos in b_concepto_original:
                self.update({
                    'conceptos_partidas': [[0, 0, {'id_partida': conceptos.id_partida, 'categoria': conceptos.categoria,
                                                    'related_categoria_padre': conceptos.related_categoria_padre,
                                                    'clave_linea': conceptos.clave_linea, 'concepto': conceptos.concepto,
                                                    'medida': conceptos.medida,
                                                    'precio_unitario': conceptos.precio_unitario,
                                                    'est_ant': 0,
                                                    'est_ant_acum': 0,
                                                    'num_est': int(1),
                                                    'numero_estimacion_group': 'Estimacion 1',
                                                    'cantidad': conceptos.cantidad}]]
                })

        else:
            b_est_tipo_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id),
                                                                  ('tipo_estimacion', '=', '1')])[-1]

            self.a_fin = b_est_tipo_est.a_fin
            
            ultima_est = b_est_tipo_est.idobra
            
            est_ant = 0
            for x in adirecta_id.conceptos_partidas: # b_est[int(c_est)-1].conceptos_partidas:
                est_ant_acum = 0

                '''busqueda3 = self.env['control.detalle_conceptos'].search(
                    [('num_est', '=', ultima_est), ('id_partida.id', '=', self.obra.id)
                        , ('clave_linea', '=', x.clave_linea), ('concepto', '=', x.concepto), ('precio_unitario', '=', x.precio_unitario),
                        ('cantidad', '=', x.cantidad)], order='num_est desc')[0] # , order='num_est desc' 
                if not busqueda3:
                    est_ant = 0
                else:
                    # for b in busqueda3:
                    est_ant = busqueda3.estimacion
                    est_ant_acum = busqueda3.estimacion + busqueda3.est_ant_acum'''
                
                self.update({
                    'conceptos_partidas': [[0, 0, {'id_partida': x.id_partida, 'categoria': x.categoria,
                                                   'related_categoria_padre': x.related_categoria_padre,
                                                   'clave_linea': x.clave_linea, 'concepto': x.concepto,
                                                   'medida': x.medida,
                                                   'precio_unitario': x.precio_unitario,
                                                   'est_ant': float(est_ant),
                                                   'est_ant_acum': float(est_ant_acum),
                                                   'num_est': int(c_est + 1),
                                                   'pendiente': float(x.cantidad) - float(est_ant_acum),
                                                   'numero_estimacion_group': 'Estimación ' + str(c_est + 1),
                                                   'cantidad': x.cantidad}]]
                })

    @api.multi
    def actualizar_conceptos(self):
        b_conceptos = self.env['partidas.partidas'].search(
            [('id', '=', self.obra.id)])

        adirecta_id = self.env['partidas.partidas'].browse(self.obra.id)

        acum = 0
        for x in self.conceptos_partidas:
            acum += 1
        c = 0
        for y in b_conceptos.conceptos_partidas:
            c += 1
            if c <= acum:
                pass
            else:
                for conceptos in adirecta_id.conceptos_partidas[int(c) - 1]:
                    self.update({
                        'conceptos_partidas': [
                            [0, 0, {'id_partida': conceptos.id_partida, 'categoria': conceptos.categoria,
                                    'related_categoria_padre': conceptos.related_categoria_padre,
                                    'clave_linea': conceptos.clave_linea, 'concepto': conceptos.concepto,
                                    'medida': conceptos.medida,
                                    'precio_unitario': conceptos.precio_unitario,
                                    'est_ant': 0,
                                    'num_est': int(self.idobra),
                                    'numero_estimacion_group': 'Estimación ' + str(self.idobra),
                                    'cantidad': conceptos.cantidad}]]
                    })

    @api.multi
    def unlink(self):
        for cp in self.conceptos_partidas:
            cp.unlink()
        for de in self.deducciones:
            de.unlink()
        if self.tipo_estimacion == "3":
            for escm in self.multiples_escalatorias:
                escm.unlink()

        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        total_programa = 0
        for i in b_programa:
            total_programa = i.total_programa
        a_fin = (self.estimado / total_programa) * 100
        self.obra.write({'a_fin': self.obra.a_fin - a_fin})

        return super(Estimaciones, self).unlink()

    @api.multi
    def ver_conceptos(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.detalle_tree_estimacion')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Conceptos',
            'res_model': 'control.detalle_conceptos',
            'view_mode': 'tree',
            'limit': 500,
            'context': {'search_default_num_est': int(self.idobra), 'search_default_id_partida': self.obra.id},
            'view_id': view.id,
        }

    @api.one
    def Estimacion(self):
        self.estimacion_id = self.id

    @api.one
    def obra_enlace(self):
        self.obra_id = self.obra

    # MONTO PROGRAMADO PARA ESTA ESTIMACION
    monto_programado_estqweb = fields.Float(digits=(12, 2), compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    diasdifqweb = fields.Integer(string='Dias de diferencia', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    dias_desfasamientoqweb = fields.Float(string='DIAS DE DESFASAMIENTO', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    monto_atrasoqweb = fields.Float(string='MONTO DE ATRASO', digits=(12, 2),
                                compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    diasperiodoqweb = fields.Float(string='Dia total del periodo', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    diasestqweb = fields.Float(string='', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    diastransestqweb = fields.Float(string='', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
    total_ret_estqweb = fields.Float(string='', digits=(12, 2), compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    porcentaje_estqweb = fields.Float(string='', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    # PORCENTAJE DE LA RETENCION TOTAL
    porc_total_retqweb = fields.Float(string='', compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    # RETENCION NETA A APLICAR EN ESTA ESTIMACION
    ret_neta_estqweb = fields.Float(string='', compute="PenasConvencionalesqweb", digits=(12, 2))  # compute="PenasConvencionales",
    # DEVOLUCION A EFECTUAR EN ESTA ESTIMACION
    # MONTO DIARIO PROGRAMADO
    montodiario_programadoqweb = fields.Float(string='MONTO DIARIO PROGRAMADO', digits=(12, 2),
                                          compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    # DIAS EJECUTADOS REALCES CON RELACION  AL MONTO DIARIO PROGRAMADO
    diasrealesrelacionqweb = fields.Float(string='DIAS EJECUTADOS REALCES CON RELACION  AL MONTO DIARIO PROGRAMADO',
                                      digits=(12, 2)
                                      , compute="PenasConvencionalesqweb")  # compute="PenasConvencionales",
    dias_transcurridosqweb = fields.Integer(compute="PenasConvencionalesqweb")
    ultimomontoqweb = fields.Float(compute="PenasConvencionalesqweb")
    sancionqweb = fields.Float(compute="PenasConvencionalesqweb")
    dias_atraso_sancionqweb = fields.Integer(compute="PenasConvencionalesqweb")

    retenido_anteriormenteqweb = fields.Float(string='', compute="retAntqweb", digits=(12, 2))  # compute="retAnt",
    devolucion_estqweb = fields.Float(string='', compute='devolucion_est_metodweb', digits=(12, 2))  # compute='devolucion_est_metodweb',

    montorealqweb = fields.Float(compute="MontoRealEstqweb", string='MONTO EJECUTADO REAL PARA ESTA ESTIMACION',
                             digits=(12, 2))  # compute="MontoRealEstqweb"

    @api.one
    def MontoRealEstqweb(self):
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        acum = 0
        for i in b_est:
            if int(i.idobra) <= int(self.idobra):
                acum = acum + i.estimado
                self.montorealqweb = acum
            else:
                print('MONTO REAL EST se paso de numero estimacion')

    @api.one
    def devolucion_est_metodweb(self):
        if self.retenido_anteriormenteqweb > self.total_ret_estqweb:
            self.devolucion_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb
        else:
            self.devolucion_estqweb = 0

    @api.one
    def retAntqweb(self):
        b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        if int(b_est_count) == 0 or int(self.idobra) == 1:
            self.retenido_anteriormenteqweb = 0
        else:
            if self.idobra:
                if b_est[int(self.idobra) - 2].total_ret_estqweb > 0:
                    ret_ant = b_est[int(self.idobra) - 2].total_ret_estqweb
                    self.retenido_anteriormenteqweb = float(ret_ant)
                else:
                    ret_ant = b_est[int(self.idobra) - 2].total_ret_estqweb * (-1)
                    self.retenido_anteriormenteqweb = float(ret_ant)
            else:
                if b_est[int(b_est_count) - 1].total_ret_estqweb > 0:
                    ret_ant = b_est[int(b_est_count) - 1].total_ret_estqweb
                    self.retenido_anteriormenteqweb = float(ret_ant)
                else:
                    ret_ant = b_est[int(b_est_count) - 1].total_ret_estqweb * (-1)
                    self.retenido_anteriormenteqweb = float(ret_ant)

    @api.one
    def PenasConvencionalesqweb(self):
        if not self.estimado:
            pass
        else:
            # FECHA INICIO ESTIMACION
            f_estimacion_inicio = self.fecha_inicio_estimacion
            # FECHA TERMINO ESTIMACION
            f_estimacion_termino = self.fecha_termino_estimacion
            # DIA DE TERMINO DE LA ESTIMACION
            f_est_termino_dia = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
            # BUSCAR FECHAS DEL PROGRAMA
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])

            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL CONTRATO
            fe1 = self.fecha_inicio_programa
            fe2 = self.fecha_termino_estimacion
            if fe1 and fe2:
                f1h = datetime.strptime(str(fe1), "%Y-%m-%d")
                f2h = datetime.strptime(str(fe2), "%Y-%m-%d")
                rh = f2h - f1h
                self.dias_transcurridosqweb = rh.days + 1

            # VERIFICAR SI EXISTE CONVENIO
            _search_cove = self.env['proceso.convenios_modificado'].search_count(
                [("nombre_contrato", "=", self.obra.nombre_contrato), ("tipo_convenio", "=", 'PL' or 'BOTH')])

            b_convenio = self.env['proceso.convenios_modificado'].search([('nombre_contrato', '=', self.obra.nombre_contrato)])
            if _search_cove > 0:
                for i in b_convenio:
                    if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                        fecha_prog = datetime.strptime(str(i.plazo_fecha_inicio), "%Y-%m-%d").date()
                        fecha_inicio_programa = fecha_prog
                        fecha_prog2 = datetime.strptime(str(i.plazo_fecha_termino), "%Y-%m-%d").date()
                        fecha_termino_programa = fecha_prog2
            else:
                # FECHA INICIO DEL PROGRAMA
                fecha_inicio_programa = b_programa.fecha_inicio_programa
                # FECHA TERMINO PROGRAMA
                fecha_termino_programa = b_programa.fecha_termino_programa

            monto_contrato = b_programa.total_programa
            # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
            diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
            acum = 0
            cont = 0
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])

            b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
            if b_est_count == 0:
                print('AUN NO HAY ESTIMACIONES')
            else:
                # QUITAR ESTO DE AQUI, CUIDADO DE NO BUGGEAR
                if int(self.idobra) == 1:
                    print('1')
                else:
                    print('2')

            # CICLO QUE RECORRE LA LISTA DE PROGRAMAS
            for i in sorted(b_programa.programa_contratos):
                cont = cont + 1
                fechatermino = i.fecha_termino
                fechainicio = i.fecha_inicio
                date_format = "%Y-%m-%d"
                fuera_mes1 = datetime.strptime(str(fechainicio), date_format)
                fuera_mes2 = datetime.strptime(str(fechatermino), date_format)
                fuera_mesr = fuera_mes2 - fuera_mes1
                fuera_mes = fuera_mesr.days + 1
                num_months = (fechainicio.year - fechatermino.year) * 12 + (fechatermino.month - fechainicio.month)
                # fecha termino del programa, mes y año
                fecha_terminop_y_m = datetime(fecha_termino_programa.year, fecha_termino_programa.month, 1)
                # fecha termino de la estimacion mes y año
                fecha_terminoest_y_m = datetime(f_estimacion_termino.year, f_estimacion_termino.month, 1)
                # ciclo de fecha termino del programa mes y año
                f_termino_proglista = datetime(fechatermino.year, fechatermino.month, 1)
                f_termino_prog_todo = datetime(fechainicio.year, fechainicio.month, fechainicio.day)
                fecha_terminoest_todo = datetime(f_estimacion_termino.year, f_estimacion_termino.month, f_estimacion_termino.day)
                # SI LA FECHA DEL TERMINO DE LA ESTIMACION ES IGUAL A LA DEL PROGRAMA HACER CALCULO FINAL
                if fecha_terminop_y_m == fecha_terminoest_y_m:
                    print('FASE FINAL')
                    acum = acum + i.monto

                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO REAL DEL PROGRAMA HASTA LA FECHA DE TERMINO DE LA ESTIMACION ACTUAL
                    dias = r.days

                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days

                    # fecha estimacion inicio, fecha desde del dia 1
                    fei = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    # fecha termino programa
                    ftp = datetime.strptime(str(fecha_termino_programa), date_format)
                    r3 = ftp - fei
                    # Contar el numero dias del inicio de la estimacion hasta el dia del termino programa
                    d_est_programatermino = r3.days

                    # FECHA TERMINACION ESTIMACION
                    fet = datetime.strptime(str(f_estimacion_termino), date_format)
                    # FECHA TERMINO PROGRAMA
                    ftp = datetime.strptime(str(fecha_termino_programa), date_format)
                    r4 = ftp - fet
                    # Contar el numero de dias desde el termino de la estimacion hasta el termino del programa
                    d_esttermino_programa = r4.days

                    f_termino_actual = datetime.strptime(str(fechainicio), date_format)
                    f_esttermino = datetime.strptime(str(f_estimacion_termino), date_format)
                    res = f_esttermino - f_termino_actual
                    dias_trans_mesactual = res.days

                    dia_inicio_prog = datetime.strptime(str(fechatermino.replace(day=1)), date_format)
                    dia_inicio_prog2 = datetime.strptime(str(fechatermino), date_format)
                    dia_inicior = dia_inicio_prog2 - dia_inicio_prog
                    dia_inicio_atermino = dia_inicior.days

                    # ultimo monto programa entre dias hasta final programa por dias del final de estimacion
                    # hasta final de programa
                    ff = d_esttermino_programa

                    ff2 = d_est_programatermino + 1
                    # FORMULA: ULTIMO MONTO / DIA INICIO MES ESTIMACION HASTA DIA TERMINO PROGRAMA * DIA TERMINO ESTIMACION
                    # HASTA DIA TERMINO PORGRAMA

                    b_programa_c = self.env['proceso.programa'].search_count([('obra.id', '=', self.obra.id)])
                    if b_programa_c == 1:
                        monto_final = (i.monto / (dias + 1)) * ff
                    elif self.idobra == 1:
                        monto_final = 0
                    else:
                        monto_final = (i.monto / (dia_inicio_atermino + 1)) * (dias_trans_mesactual + 1)

                    m_estimado = (acum - i.monto) + monto_final

                    self.ultimomontoqweb = monto_final

                    self.diasestqweb = diasest
                    self.diastransestqweb = ff2

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_estqweb = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdifqweb = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodoqweb = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO

                    self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if self.montodiario_programadoqweb == 0:
                        self.montodiario_programadoqweb = 1
                    self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb

                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                        self.dias_desfasamientoqweb = 0
                    else:
                        self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb

                    # MONTO DE ATRASO
                    self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb

                    # PORCENTAJE ESTIMADO
                    self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100

                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb

                    self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100

                    f_sansion_est = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                             f_estimacion_termino.day)
                    f_sansion_prog = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                              fecha_termino_programa.day)
                    if f_sansion_est > f_sansion_prog:
                        print(' APLICAR SANCION x')
                        acum_ret = 0
                        termino_periodo_s = datetime.strptime(str(fecha_termino_programa), date_format)
                        termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), date_format)
                        for u in b_est:
                            if int(u.idobra) <= int(self.idobra) or int(u.idobra) <= int(b_est_count + 1):
                                if u.ret_neta_est < 0:
                                    acum_ret += u.ret_neta_est
                                else:
                                    pass
                                if u.sancion > 0:
                                    acum_ret = 0
                                resta = termino_estimacion_s - termino_periodo_s
                                dias_sancion = resta.days
                                if dias_sancion == 0:
                                    dias_sancion = 1
                                sancion = (self.estimado + ((acum_ret - u.ret_neta_est) * -1)) * (
                                        dias_sancion * 0.03)  # self.obra.numero_contrato.retencion)
                                self.sancionqweb = sancion
                                self.ret_neta_estqweb = self.retenido_anteriormenteqweb
                                self.dias_atraso_sancionqweb = dias_sancion

                            else:
                                pass
                    else:
                        if self.retenido_anteriormenteqweb == 0:
                            self.ret_neta_estqweb = self.total_ret_estqweb * -1

                        elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                            self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                        elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                            self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                # SI EL PROGRAMA ES UNICO Y DE VARIOS MESES
                elif int(num_months) > 2:
                    acum = acum + i.monto
                    # dias transcurridos
                    f_termino_esti = datetime.strptime(str(f_estimacion_termino), date_format)
                    f_inicio_prog = datetime.strptime(str(fecha_inicio_programa), date_format)
                    r_diastrans = f_termino_esti - f_inicio_prog
                    dias_trans = r_diastrans.days + 1
                    m_estimado = (acum / fuera_mes) * dias_trans
                    # self.diasestqweb = diasestx
                    self.diastransestqweb = dias_trans

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_estqewb = m_estimado

                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                    # TERMINO DE LA ESTIMACION
                    dias = r.days + 1
                    self.diasdifqweb = dias

                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    # DIAS DEL PERIODO
                    total_dias_periodo = r2.days
                    self.diasperiodoqweb = total_dias_periodo

                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    # EVITAR EXCEPCION
                    if self.montorealqweb == 0 or self.montodiario_programadoqweb == 0:
                        self.montorealqweb = 1
                        self.montodiario_programadoqweb = 1

                    self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                        self.dias_desfasamientoqweb = 0
                    else:
                        self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                    # MONTO DE ATRASO
                    self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb
                    self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100
                    f_sansion_est = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                             f_estimacion_termino.day)
                    f_sansion_prog = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                              fecha_termino_programa.day)
                    if f_sansion_est > f_sansion_prog:
                        print(' APLICAR SANCION x')
                        acum_ret = 0
                        termino_periodo_s = datetime.strptime(str(fecha_termino_programa), date_format)
                        termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), date_format)
                        for u in b_est:
                            if int(u.idobra) <= int(self.idobra) or int(u.idobra) <= int(b_est_count + 1):
                                if u.ret_neta_est < 0:
                                    acum_ret += u.ret_neta_est
                                else:
                                    pass
                                if u.sancion > 0:
                                    acum_ret = 0
                                resta = termino_estimacion_s - termino_periodo_s
                                dias_sancion = resta.days
                                if dias_sancion == 0:
                                    dias_sancion = 1
                                sancion = (self.estimado + ((acum_ret - u.ret_neta_est) * -1)) * (
                                        dias_sancion * 0.03)  # self.obra.numero_contrato.retencion)
                                self.sancionqweb = sancion
                                self.ret_neta_estqweb = self.retenido_anteriormenteqweb
                                self.dias_atraso_sancionqweb = dias_sancion
                            else:
                                pass
                    else:
                        if self.retenido_anteriormenteqweb == 0:
                            self.ret_neta_estqweb = self.total_ret_estqweb * -1

                        elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                            self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                        elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                            self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
                elif f_est_termino_dia.day == diasest:
                    # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                    if f_termino_proglista <= fecha_terminoest_y_m: #elif
                        acum = acum + i.monto
                        print('CUANDO LA ESTIMACION ES IGUAL AL DIA DEL ULTIMO MES')
                        f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                        f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r = f2 - f1
                        dias = r.days

                        f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                        f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                        r2 = f4 - f3
                        total_dias_periodo = r2.days

                        diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                        f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                        f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r4 = f8 - f7
                        diastransest = r4.days

                        m_estimado = acum
                        self.diasestqweb = diasest
                        self.diastransestqweb = diastransest

                        # MONTO PROGRAMADO PARA ESTA ESTIMACION
                        self.monto_programado_estqweb = m_estimado
                        # self.reduccion = monto_final
                        # DIAS DE DIFERENCIA ENTRE EST
                        self.diasdifqweb = dias + 1
                        # TOTAL DIAS PERIODO PROGRAMA
                        self.diasperiodoqweb = total_dias_periodo
                        # MONTO DIARIO PROGRAMADO
                        self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                        # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                        if self.montodiario_programadoqweb == 0:
                            self.montodiario_programadoqweb = 1

                        self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                        # DIAS DE DESFASAMIENTO
                        if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                            self.dias_desfasamientoqweb = 0
                        else:
                            self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                        # MONTO DE ATRASO
                        self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                        # PORCENTAJE ESTIMADO
                        self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100
                        # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        # %
                        self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb
                        self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100

                        f_sansion_est = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                                 f_estimacion_termino.day)
                        f_sansion_prog = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                                  fecha_termino_programa.day)

                        if f_sansion_est > f_sansion_prog:
                            print(' APLICAR SANCION x')
                            acum_ret = 0
                            termino_periodo_s = datetime.strptime(str(fecha_termino_programa), date_format)
                            termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), date_format)
                            for u in b_est:
                                if int(u.idobra) <= int(self.idobra) or int(u.idobra) <= int(b_est_count + 1):
                                    if u.ret_neta_est < 0:
                                        acum_ret += u.ret_neta_est
                                    else:
                                        pass
                                    if u.sancion > 0:
                                        acum_ret = 0
                                    resta = termino_estimacion_s - termino_periodo_s
                                    dias_sancion = resta.days
                                    if dias_sancion == 0:
                                        dias_sancion = 1
                                    sancion = (self.estimado + ((acum_ret - u.ret_neta_est) * -1)) * (
                                            dias_sancion * 0.03)  # self.obra.numero_contrato.retencion)
                                    self.sancionqweb = sancion
                                    self.ret_neta_estqweb = self.retenido_anteriormenteqweb
                                    self.dias_atraso_sancionqweb = dias_sancion

                                else:
                                    pass
                        else:
                            if self.retenido_anteriormenteqweb == 0:
                                self.ret_neta_estqweb = self.total_ret_estqweb * -1

                            elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                                self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                            elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                                self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                    else:
                        print('no')
                # SI EL TERMINO DE LA ESTIMACION ES MENOR AL DIA TOTAL DEL MES ENTONCES SE MODIFICARA EL MONTO ACUMULADO
                # CON UNA FORMULA PARA CALCULAR EL MONTO ACTUAL HASTA LA FECHA DE TERMINO DE LA ESTIMACION
                elif f_est_termino_dia.day < diasest:
                    if f_termino_proglista > fecha_terminoest_y_m:
                        print('se paso de fecha 2')

                    # SON MESES DIFERENTES
                    elif f_estimacion_inicio.month is not f_estimacion_termino.month:
                        print('#1 EL MES FECHA EST INICIO ES DIFERENTE AL MES EST TERMINO')
                        esti = self.env['control.estimaciones'].search(
                            [('obra.id', '=', self.obra.id)])

                        if fecha_terminoest_y_m == fecha_terminop_y_m:
                            for x in esti:
                                if x.idobra > self.idobra:
                                    # SI NO ES LA ULTIMA ESTIMACION ENTONCES
                                    pass

                                elif x.idobra == self.idobra:
                                    print('#2 COINCIDE CON EL ULTIMO MES DEL PROGRAMA CUANDO SON MESES DIFERENTES')
                                    diasestx = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                        1]
                                    fx = datetime.strptime(str(f_estimacion_inicio), date_format)
                                    fy = datetime.strptime(str(f_estimacion_termino), date_format)
                                    rx = fy - fx
                                    # DIAS TRANSCURRIDOS DE LA ESTIMACION
                                    diastransestx = rx.days
                                    # MONTO CORRESPONDIENTE A LA FECHA DE ESTIMACION CON LA DEL PROGRAMA
                                    ultimo_monto = i.monto
                                    x1 = acum - ultimo_monto
                                    x2 = i.monto / diasestx
                                    m_estimado = x1 + x2 * (diastransestx + 1)

                                    self.diasestqweb = diasestx
                                    self.diastransestqweb = diastransestx

                                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                    self.monto_programado_estqweb = m_estimado

                                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                    r = f2 - f1
                                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                                    # TERMINO DE LA ESTIMACION
                                    dias = r.days + 1
                                    self.diasdifqweb = dias

                                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                                    r2 = f4 - f3
                                    # DIAS DEL PERIODO
                                    total_dias_periodo = r2.days
                                    self.diasperiodoqweb = total_dias_periodo

                                    # MONTO DIARIO PROGRAMADO
                                    self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                    self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                                    # DIAS DE DESFASAMIENTO
                                    if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                                        self.dias_desfasamientoqweb = 0
                                    else:
                                        self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                                    # MONTO DE ATRASO
                                    self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                                    # PORCENTAJE ESTIMADO
                                    self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100
                                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                    self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb
                                    self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100
                                    # RETENCION
                                    if self.ret_neta_estqweb == 0:
                                        self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb
                                    elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                                        self.ret_neta_estqweb = self.total_ret_estqweb - self.retenido_anteriormenteqweb

                                    elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                                        self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb
                            pass
                        else:
                            acum = acum + i.monto
                            f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                            f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                            r = f2 - f1
                            # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA TERMINO EST
                            dias = r.days

                            f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                            f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                            r2 = f4 - f3
                            # DIAS DEL PERIODO
                            total_dias_periodo = r2.days

                            # ---------------------
                            # CUANTOS DIAS TIENE EL MES DE LA FECHA ESTIMADA
                            diasest = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[1]
                            dia_mes_termino = \
                            calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]

                            dat = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                           f_estimacion_termino.day)
                            dat4 = datetime(f_estimacion_inicio.year, f_estimacion_inicio.month,
                                            f_estimacion_inicio.day)
                            dat2 = datetime(fechatermino.year, fechatermino.month, fechatermino.day)

                            f_sansion = datetime(fecha_termino_programa.year, fecha_termino_programa.month,
                                                 fecha_termino_programa.day)
                            # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MAYOR A LA FECHA DEL TERMINO DEL PROGRAMA
                            if dat > dat2:
                                print('CUANDO LA FECHA DE TERMINO DE EST ES MAYOR A LA DEL TERMINO DEL PROGRAMA')
                                cx = 0
                                acum_ftemtp = 0
                                for c in b_programa.programa_contratos:
                                    dat3 = datetime(c.fecha_termino.year,
                                                    c.fecha_termino.month,
                                                    c.fecha_termino.day)
                                    if dat == dat3:
                                        pass
                                    elif dat > f_sansion:  # antes era dat4 verificar 08/04/20
                                        pass
                                    elif dat3 > dat:
                                        pass
                                    elif dat3 <= dat:
                                        acum_ftemtp += c.monto
                                        cx += 1

                                ultimo_monto = b_programa.programa_contratos[int(cx)].monto

                                f_pt = datetime.strptime(str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                                         date_format)
                                f_et = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = f_et - f_pt
                                d_entre_fecha = ry.days

                                ff_inicio = datetime.strptime(str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                                              date_format)
                                ff_termino = datetime.strptime(
                                    str(b_programa.programa_contratos[int(cx)].fecha_termino), date_format)
                                rf = ff_termino - ff_inicio
                                diastransestx = rf.days + 1
                                # print(d_entre_fecha, 'FECHA')
                                formula = (ultimo_monto / diastransestx) * (d_entre_fecha + 1)
                                acumulado = acum_ftemtp
                                m_estimado = acumulado + formula  # * (diastransest + 1)

                                self.ultimomontoqweb = ultimo_monto
                                self.diasestqweb = diasest
                                self.diastransestqweb = diastransestx

                                # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                self.monto_programado_estqweb = m_estimado
                                # DIAS DE DIFERENCIA ENTRE EST
                                self.diasdifqweb = dias + 1
                                # TOTAL DIAS PERIODO PROGRAMA
                                self.diasperiodoqweb = total_dias_periodo
                                # MONTO DIARIO PROGRAMADO
                                self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                                if self.montodiario_programadoqweb == 0:
                                    self.montodiario_programadoqweb = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                                # DIAS DE DESFASAMIENTO
                                if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                                    self.dias_desfasamientoqweb = 0
                                else:
                                    self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                                # MONTO DE ATRASO
                                self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                                # PORCENTAJE ESTIMADO
                                self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                # %
                                self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb

                                self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100

                                if self.retenido_anteriormenteqweb == 0:
                                    self.ret_neta_estqweb = self.total_ret_estqweb

                                elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                                    self.ret_neta_estqweb = self.total_ret_estqweb - self.retenido_anteriormenteqweb

                                elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                                    self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                                # return acumulado
                            # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MENOR A LA FECHA DEL TERMINO DEL PROGRAMA
                            elif dat < dat2:
                                ultimo_monto = i.monto

                                ffx = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                                ffx2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = ffx2 - ffx
                                diastransest = ry.days + 1

                                _programa_cx = self.env['proceso.programa'].search_count(
                                    [('obra.id', '=', self.obra.id)])
                                if _programa_cx == 1:
                                    x1 = acum
                                else:
                                    x1 = acum - ultimo_monto
                                # formula = (i.monto / dia_mes_termino) * (dia_mes_termino - diastransest) cambio el 09/04/20
                                formula = (i.monto / dia_mes_termino) * diastransest  # SIDUR-ED-19-078.1698

                                if _programa_cx == 1:
                                    m_estimado = x1 - formula
                                else:
                                    m_estimado = x1 + formula

                                self.ultimomonto = ultimo_monto

                                self.diasestqweb = diasest
                                self.diastransestqweb = diastransest
                                # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                self.monto_programado_estqweb = m_estimado
                                # DIAS DE DIFERENCIA ENTRE EST
                                self.diasdifqweb = dias + 1
                                # TOTAL DIAS PERIODO PROGRAMA
                                self.diasperiodoqweb = total_dias_periodo
                                # MONTO DIARIO PROGRAMADO
                                self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                                if self.montodiario_programadoqweb == 0:
                                    self.montodiario_programadoqweb = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                                # DIAS DE DESFASAMIENTO
                                if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                                    self.dias_desfasamiento = 0
                                else:
                                    # self.dias_desfasamiento = self.dias_transcurridos - self.diasrealesrelacion
                                    self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                                # MONTO DE ATRASO
                                self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                                # PORCENTAJE ESTIMADO
                                self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb
                                self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100
                                if self.retenido_anteriormenteqweb == 0:
                                    self.ret_neta_estqweb = self.total_ret_estqweb * -1

                                elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                                    self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                                elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:                            
                                    self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                elif f_termino_prog_todo <= fecha_terminoest_todo:
                    acum = acum + i.monto
                    print('CUANDO LA ESTIMACION ES MENOS DE 30 DIAS EN EL MES')

                    f1 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO
                    dias = r.days + 1
                    # dia 0 del mes al dia de inicio de esti
                    dia_0 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    dia_02 = datetime.strptime(str(f_estimacion_inicio), date_format)
                    dia_r = dia_02 - dia_0
                    dia_rr = dia_r.days

                    dia_inicioprog = datetime.strptime(str(fechainicio.replace(day=1)), date_format)
                    dia_terminprog = datetime.strptime(str(fechatermino), date_format)
                    dia_progx = dia_terminprog - dia_inicioprog
                    dia_progy = dia_progx.days + 1

                    fg = datetime.strptime(str(f_estimacion_inicio), date_format)
                    fh = datetime.strptime(str(f_estimacion_termino), date_format)
                    rx = fh - fg
                    # DIAS TRANSCURRIDOS DE LA ESTIMACION
                    diasx = rx.days + 1
                    # DIAS DEL PERIODO
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days
                    # ---------------------
                    # DIAS DEL MES DE LA ESTIMACION
                    diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]

                    f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                    f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r4 = f8 - f7
                    # DIAS DESDE EL INICIO DEL MES DE LA ESTIMACION HASTA EL TERMINO
                    diastransest = r4.days + 1
                    # -------------------------
                    # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                    # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                    if fechatermino < f_estimacion_termino:
                        formula = 1  # evitar errores
                    else:
                        if diastransest == diasest:
                            # print(' termina en el dia ultimo del mes', diastransest, diasest)
                            # MONTO / DIAS DEL MES * NUMERO DE DIAS TRANSCURRIDOS DEL INICIO DEL MES DE LA EST AL TERMINO
                            formula = (i.monto / diasest) * diastransest
                        elif dia_progy < diasest:

                            formula = (i.monto / dia_progy) * diasx # SIDUR-PF-18-220.1497
                        else:
                            formula = (i.monto / diasest) * dias # SIDUR-ED-20-002.1873

                    self.ultimomontoqweb = i.monto
                    if str(self.idobra) == '1' or int(b_est_count) == 0:
                        m_estimado = formula
                    else:
                        m_estimado = (acum - i.monto) + formula  # (i.monto - formula)

                    self.diasestqweb = diasest
                    self.diastransestqweb = diastransest + 1

                    fv = datetime.strptime(str(fecha_inicio_programa), date_format)
                    fvv = datetime.strptime(str(f_estimacion_termino), date_format)
                    rxx = fvv - fv
                    diasf = rxx.days

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_estqweb = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdifqweb = diasf + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodoqweb = total_dias_periodo

                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programadoqweb = self.monto_programado_estqweb / self.diasdifqweb
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if self.montodiario_programadoqweb == 0:
                        self.montodiario_programadoqweb = 1
                    self.diasrealesrelacionqweb = self.montorealqweb / self.montodiario_programadoqweb
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridosqweb <= self.diasrealesrelacionqweb:
                        self.dias_desfasamientoqweb = 0
                    else:
                        self.dias_desfasamientoqweb = self.diasdifqweb - self.diasrealesrelacionqweb
                    # MONTO DE ATRASO
                    self.monto_atrasoqweb = self.dias_desfasamientoqweb * self.montodiario_programadoqweb
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_estqweb = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    # %
                    self.porc_total_retqweb = self.retencion * self.dias_desfasamientoqweb
                    self.total_ret_estqweb = (self.monto_atrasoqweb * self.porc_total_retqweb) / 100

                    if self.ret_neta_estqweb == 0:
                        self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                    elif self.retenido_anteriormenteqweb <= self.total_ret_estqweb:
                        self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb

                    elif self.retenido_anteriormenteqweb > self.total_ret_estqweb:
                        self.ret_neta_estqweb = self.retenido_anteriormenteqweb - self.total_ret_estqweb
                else:
                    print('no x2')
            else:
                print('se termino el cliclo')


class Detalleconceptos(models.Model):
    _name = 'control.detalle_conceptos'

    id_sideop = fields.Integer('ID SIDEOP CATALOGO') # importacion id_sideop
    num_est = fields.Integer('Numero de Estimación', store=True)
    numero_estimacion_group = fields.Char('Numero de Estimación')
    # verifica si la categoria tiene padre, auxiliar para decorador de tree view
    related_categoria_padre = fields.Many2one('catalogo.categoria', store=True) # related="categoria.parent_id",
    # clave
    categoria = fields.Many2one('catalogo.categoria', 'Categoria', )
    descripcion = fields.Text('Descripción')
    name = fields.Many2one('catalogo.categoria', 'Categoria Padre')
    clave_linea = fields.Char('Clave', store=True)
    concepto = fields.Text(store=True)
    medida = fields.Char(store=True)
    precio_unitario = fields.Float(store=True)
    cantidad = fields.Float(store=True)
    # CONCEPTOS EJECUTADOS EN EL PERIODO
    est_ant = fields.Float(string="Est. Ant", store=True)
    est_ant_acum = fields.Float(string="Est. Ant Acum", store=True)
    pendiente = fields.Float(string="Pendiente", required=False, store=True)
    estimacion = fields.Float(string="Estimacion", required=False, digits=(12, 5), store=True)
    importe_ejecutado = fields.Float(string="Importe", required=False, store=True, digits=(12, 2))
    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", readonly=True,
                                 store=True)
    # importe = fields.Float(compute="sumaCantidad")
    # MODIFICACIONES
    fecha_modificacion = fields.Date('Fecha de la Modificación')
    justificacion = fields.Text('Justificación de Modificación')

    @api.multi
    @api.onchange('estimacion')
    def Pendiente(self):
        estimacion = int(self.num_est) - 1
        busqueda = self.env['control.detalle_conceptos'].search(
            [('num_est', '=', estimacion), ('id_partida.id', '=', self.id_partida.id)
                , ('clave_linea', '=', self.clave_linea), ('concepto', '=', self.concepto),
             ('precio_unitario', '=', self.precio_unitario), ('cantidad', '=', self.cantidad)])

        busqueda2 = self.env['control.detalle_conceptos'].search(
            [('num_est', '<', int(self.num_est)), ('id_partida.id', '=', self.id_partida.id)
                , ('clave_linea', '=', self.clave_linea), ('concepto', '=', self.concepto),
             ('precio_unitario', '=', self.precio_unitario), ('cantidad', '=', self.cantidad)])
        est_ant = 0
        for i in busqueda:
            est_ant = i.estimacion

        est_ant_acum = 0

        for x in busqueda2:
            est_ant_acum += x.estimacion

        self.est_ant = est_ant
        self.est_ant_acum = est_ant_acum  # + b.estimacion,
        self.pendiente = self.cantidad - (est_ant_acum + self.estimacion)

    @api.multi
    @api.onchange('precio_unitario', 'estimacion')
    def importeEjec(self):
        self.importe_ejecutado = self.estimacion * self.precio_unitario


class Deducciones(models.Model):
    _name = 'control.deducciones'
    # importacion
    id_sideop = fields.Integer()

    estimacion = fields.Many2one('control.estimaciones', 'id hacia estimaciones para conexion', store=True)

    name = fields.Char(store=True)
    porcentaje = fields.Float(store=True)
    valor = fields.Float(digits=(12,2), store=True)
    # valor = fields.Float(store=True)


class OrdenesCambio(models.Model):
    _name = 'control.ordenes_cambio'
    _rec_name = 'orden_pago'

    observaciones_ = fields.Text('OBSERVACIONES')
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="numero_contrato.obra.obra_planeada.ejercicio")
    clave_obra = fields.Char()
    orden_pago = fields.Char(string='Orden de pago', size=10)
    doc_logistico = fields.Char(string='Doc logístico', size=10)
    orden_compra = fields.Char(string='Orden de compra', size=10)
    vinculo_estimaciones = fields.Many2one('control.estimaciones', string='Estimación id') # ID DE ESTIMACION
    no_estimacion = fields.Char(string='# Estimación', related="vinculo_estimaciones.idobra")
    numero_contrato = fields.Many2one('partidas.partidas', string='Contrato', ) # NUMERO DE CONTRATO DE PARTIDA

    dias_transcurridos = fields.Integer('Dias transcurridos', )

    select_color = [('Rojo', 'Rojo')]
    color_orden = fields.Selection(select_color, string="Estado de Orden", )

    activador_color = fields.Boolean(string="activador", )

    '''@api.one
    def color_ordenes(self):
        today = date.today()
        hoy = str(today.strftime("%Y-%m-%d"))
        fecha_exp = datetime.strptime(str(self.fecha), "%Y-%m-%d")
        fecha_actual = datetime.strptime(str(hoy), "%Y-%m-%d")
        r = fecha_actual - fecha_exp

        self.dias_transcurridos = r.days + 1

        if self.estatus_orden_pago == 'orden_pago' or self.estatus_orden_pago == 'recibido':
            if self.dias_transcurridos > 21:
                self.color_orden = 'Rojo'
                self.activador_color = True
            else:
                self.color_orden = ''
                self.activador_color = False
        elif self.estatus_orden_pago == 'pagado':
            self.color_orden = ''
            self.activador_color = False'''

    @api.onchange('vinculo_estimaciones')
    def _numero_contrato(self):
        self.numero_contrato = self.vinculo_estimaciones.obra.id

    @api.onchange('orden_pago')
    def actualizar_orden(self):
        if not self.orden_pago:
            pass
        else:
            b_est = self.env['control.estimaciones'].browse(self.vinculo_estimaciones.id)
            dato = {
                'con_orden': True
            }
            listax = b_est.write(dato)

    @api.multi
    @api.onchange('fecha_pago')
    def actualizar_dato(self):
        if not self.fecha_pago:
            pass
        else:
            # b_est = self.env['control.estimaciones'].browse(self.vinculo_estimaciones.id)
            b_monto = self.env['control.ordenes_cambio'].search([('numero_contrato.id', '=', self.numero_contrato.id)])
            search_est = self.env['control.estimaciones'].search([('obra.id', '=', self.numero_contrato.id)])
            b_partida = self.env['partidas.partidas'].search([('id', '=', self.numero_contrato.id)])
            acum = 0

            acum_est = 0
            for x in search_est:
                acum_est += x.a_pagar

            acum_ant = 0
            for i in b_monto:
                if self.tipo_pago == 'Pago':
                    if i.fecha_pago:
                        acum_ant += i.monto_total_
                    else:
                        pass
                else:
                    if i.fecha_pago:
                        acum += i.monto_total_
                    else:
                        pass
            x = acum
            x_ant = acum_ant
            anticipo_pagado = False
            if self.tipo_pago == 'Pago': # PAGO ANTICIPO
                if b_partida.total_anticipo == x_ant:
                    anticipo_pagado = True
                else:
                    anticipo_pagado = False
                b_obra = self.env['partidas.partidas'].browse(self.numero_contrato.id)
                datos = {'anticipo_pagado': anticipo_pagado, 'pagado_anticipo': x_ant}
                lista = b_obra.write(datos)
            else: # PAGO ESTIMACION
                if acum == acum_est:
                    estimado_pagado = True
                else:
                    estimado_pagado = False
                b_obra = self.env['partidas.partidas'].browse(self.numero_contrato.id)
                datos = {'estimado_pagado': estimado_pagado, 'pagado_estimacion': x, 'total_estimado': acum_est}
                lista = b_obra.write(datos)

    fecha = fields.Date(string='Fecha de expedición', required=True)
    monto_total = fields.Float(string='Monto neto a pagar', required=True) # IMPORTE LIQUIDO
    monto_total_ = fields.Float(string='Monto Total')

    @api.onchange('vinculo_estimaciones')
    def _monto_total(self):
        self.monto_total = self.vinculo_estimaciones.a_pagar

    @api.onchange('numero_contrato')
    def _monto_total(self):
        self.monto_total = self.numero_contrato.total_anticipo

    # cuentas_bancos = fields.Many2one('control.cuentasbancos', required=True, string='Fondo')
    programa_inversion = fields.Many2one('generales.programas_inversion', string='Fondo')
    fecha_recibido = fields.Date(string='Fecha de recibido')
    fecha_pago = fields.Date(string='Fecha de pago')

    contratista_contrato = fields.Many2one(related="numero_contrato.contratista")
    a_pagar = fields.Float(string="Importe liquido:", required=False, related='vinculo_estimaciones.a_pagar')
    #Pendiente field recurso
    obra = fields.Many2one(related='numero_contrato.obra', string='Obra:', readonly=True) # OBRA DE LA PARTIDA

    amort_anticipo = fields.Float(related="vinculo_estimaciones.amort_anticipo")
    monto_contrato = fields.Float(related="numero_contrato.total")

    # AGREGAR PAGO FINIQUITO
    radio_pago = [(
        'Estimacion', "Estimacion"), ('Pago', "Pago de Anticipo")]
    tipo_pago = fields.Selection(radio_pago, string="Tipo de Pago")

    @api.constrains('orden_pago')
    def _validar_lenorderpago(self):
        if len(str(self.orden_pago)) < 10:
            raise Warning("La orden de pago debe de ser de 10 digitos.")

    '''@api.constrains('doc_logistico')
    def _validar_doc_logistico(self):
        if len(str(self.doc_logistico)) < 10:
            raise Warning("El doc logístico debe de ser de 10 digitos.")

    @api.constrains('orden_compra')
    def _validar_orden_compra(self):
        if len(str(self.orden_compra)) < 10:
            raise Warning("La orden de compra debe de ser de 10 digitos.")'''

    estatus_orden_pago = fields.Selection(
        [('orden_pago', 'Expedida'), ('recibido', 'Recibido'), ('pagado', 'Pagado'), ],
        default='orden_pago', store=True)

    # CUANDO SE CANCELE UN PAGO LOS VALORES VOLVERAN A 0 O FALSE
    @api.multi
    def borrador_progressbar(self):
        # ACTUALIZAR ESTADO ORDEN ESTIMACION
        b_est = self.env['control.estimaciones'].browse(self.vinculo_estimaciones.id)
        dato = {
            'con_orden': False
        }
        listax = b_est.write(dato)
        # ACTUALIZAR MONTO PARTIDA
        b_est = self.env['control.ordenes_cambio'].search([('numero_contrato.id', '=', self.numero_contrato.id)])
        b_partida = self.env['partidas.partidas'].search([('id', '=', self.numero_contrato.id)])
        acum = 0
        for i in b_est:
            acum += i.monto_total
        x = b_partida.pagado_estimacion - acum

        b_obra = self.env['partidas.partidas'].browse(self.numero_contrato.id)
        datos = {'estimado_pagado': False, 'pagado_estimacion': x}
        lista = b_obra.write(datos)
        self.write({'estatus_orden_pago': 'orden_pago'})

    @api.model
    def create(self, values):
        b_est = self.env['control.estimaciones'].browse(values['vinculo_estimaciones'])
        dato = {
            'con_orden': True
        }
        b_est.write(dato)
        return super(OrdenesCambio, self).create(values)

    @api.multi
    def confirmado_progressbar(self):
        self.write({'estatus_orden_pago': 'recibido'})
        # VISTA OBJETIVO
        view = self.env.ref('Finanzas.orden_cambio_form_fecha_recibido')  # Vista del Formulario al que quieres apuntar

        search = self.env['control.ordenes_cambio'].search([('orden_pago', '=', self.orden_pago)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA

        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes de pago',
            'res_model': 'control.ordenes_cambio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': search.id,
        }

    @api.multi
    def validado_progressbar(self):
        self.write({'estatus_orden_pago': 'pagado'})
        # VISTA OBJETIVO
        view = self.env.ref(
            'Finanzas.orden_cambio_form_fecha_pago')  # Vista del Formulario al que quieres apuntar

        search = self.env['control.ordenes_cambio'].search([('orden_pago', '=', self.orden_pago)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA

        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes de pago',
            'res_model': 'control.ordenes_cambio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'res_id': search.id,
        }

    '''@api.onchange('fecha_pago')
    def onchange_fecha_pagado(self):
        if not self.fecha_pago:
            pass
        else:
            self.write({'estatus_orden_pago': 'pagado'})'''

    '''@api.onchange('fecha_recibido')
    def onchange_fecha_recibido(self):
        if not self.fecha_recibido:
            pass
        else:
            self.write({'estatus_orden_pago': 'recibido'})
            self.write({'estatus_orden_pago': 'orden_pago'})'''


