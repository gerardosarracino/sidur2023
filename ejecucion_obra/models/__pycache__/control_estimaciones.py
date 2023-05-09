from odoo import models, fields, api, exceptions
from datetime import date
from datetime import datetime
import calendar
from odoo.exceptions import ValidationError


class Estimaciones(models.Model):
    _name = 'control.estimaciones'
    _rec_name = 'idobra'

    id_sideop = fields.Integer('ID SIDEOP')
    num_contrato = fields.Char('ID contrato SIDEOP')

    # NUMERO DE ESTIMACION
    idobra = fields.Char(string="Numero de Estimacion:")
    # ID ESTIMACION
    ide_estimacion = fields.Char(string="ID", compute="estid")
    # VER SI UTILIZAR
    estimacion_id = fields.Char()

    obra = fields.Many2one('partidas.partidas', string='Obra:', readonly=True)
    obra_id = fields.Char(compute="obra_enlace", store=True)

    # ver si utilizar
    p_id = fields.Integer("ID PARTIDA", related="obra.p_id")

    # AUXILIAR DE CONEXION HACIA CONTRATO
    numero_contrato = fields.Many2one(string="nc", related="obra.numero_contrato")
    descripcion_contrato = fields.Text(related="numero_contrato.name")
    nombre_partida = fields.Many2one(related="obra.obra")

    # ESTIMACIONES
    radio_estimacion = [(
        '1', "Estimacion"), ('2', "Escalatoria")]
    tipo_estimacion = fields.Selection(radio_estimacion, string="")

    # estimacions_id = fields.Char(compute="estimacionId", store=True)
    numero_estimacion = fields.Char(string="Número de Estimación:")
    # ESTIMACIONES ESCALATORIAS
    estimacion_esc = fields.Many2one('control.estimaciones', string="Selecciona la estimacion a escalar")
    sub_total_esc = fields.Float('Subtotal de escalatoria Padre', related="estimacion_esc.estimacion_subtotal")
    sub_total_esc_h = fields.Float('Subtotal Escalatoria')
    por_escalatoria = fields.Float('Ingresar el % de escalatoria')

    # METODO PARA CALCULAR SUBTOTAL DE LA ESCALATORIA
    @api.multi
    @api.onchange('por_escalatoria')
    def subtotal_escalatoria(self):
        self.sub_total_esc_h = (self.por_escalatoria * self.sub_total_esc) + self.sub_total_esc

    fecha_inicio_estimacion = fields.Date(string="Del:", default=fields.Date.today())
    fecha_termino_estimacion = fields.Date(string="Al:", default=fields.Date.today())
    fecha_presentacion = fields.Date(string="Fecha de presentación:", default=fields.Date.today())
    fecha_revision = fields.Date(string="Fecha revisión Residente:",  default=fields.Date.today())

    radio_aplica = [(
        '1', "Estimación Finiquito"), ('2', "Amortizar Total Anticipo	")]
    si_aplica = fields.Selection(radio_aplica, string="")

    notas = fields.Text(string="Notas:", required=False, )

    # DEDUCCIONES
    deducciones = fields.Many2many('control.deducciones', string="Deducciones:", )

    # CALCULO DE LA ESTIMACION
    estimado = fields.Float(string="Importe ejecutado estimación:", required=False )
    amort_anticipo = fields.Float(string="Amortización de Anticipo:", compute="amortizacion_anticipo")

    # amort_anticipo_partida = fields.Float(related="obra.numero_contrato.contrato_partida_adjudicacion.porcentaje_anticipo")
    # % anticipo de amort. estimacion
    amort_anticipo_partida = fields.Float(default=0.30)

    estimacion_subtotal = fields.Float(string="Neto Estimación sin IVA:", compute="Estimacion_sinIva")
    estimacion_iva = fields.Float(string="I.V.A. 16%", compute="Estimacion_Iva")
    estimacion_facturado = fields.Float(string="Neto Estimación con IVA:", compute="Estimacion_conIva")
    estimado_deducciones = fields.Float(string="Menos Suma Deducciones:", required=False, )

    ret_dev = fields.Float(string="Retención/Devolución:", required=False, )
    sancion = fields.Float(string="Sanción por Incump. de plazo:", required=False, )

    a_pagar = fields.Float(string="Importe liquido:", required=False, compute="Importe_liquido")

    # PENAS CONVENCIONALES
    menos_clau_retraso = fields.Float(string="Menos Clausula Retraso:", required=False, )
    sancion_incump_plazo = fields.Integer(string="Sanción por Incump. de plazo:", required=False, )

    # CONCEPTOS EJECUTADOS
    conceptos_partidas = fields.Many2many('proceso.conceptos_part', compute="conceptosEjecutados", store=True)
    total_conceptos = fields.Float(string="Total:",  required=False)

    # ID DE LA ESTIMACION
    estimacion_ids = fields.Char(string="ID")

    # IVA
    b_iva = fields.Float(string="IVA DESDE CONFIGURACION", compute="BuscarIva")

    # DATOS DEL CONTRATO PARA REPORTE
    fecha_contrato = fields.Date(string="", related="obra.fecha", )
    monto_contrato = fields.Float(string="", related="obra.total_partida", )
    anticipo_contrato = fields.Float(string="", related="obra.total_anticipo", )
    fechainicio_contrato = fields.Date(string="", related="obra.fechainicio", )
    fechatermino_contrato = fields.Date(string="", related="obra.fechatermino", )
    municipio_contrato = fields.Many2one(string="", related="obra.municipio", )
    tipobra_contrato = fields.Many2one(string="", related="obra.obra.obra_planeada.tipoObra", )
    contratista_contrato = fields.Many2one(string="", related="obra.contratista", )
    programa = fields.Many2one(string="", related="obra.programaInversion", )
    subdirector_contrato = fields.Char(string="", compute="BuscarDirector")
    # DATOS Y CAMPOS CALCULADOS PARA REPORTE DE RETENCION
    fecha_inicio_programa = fields.Date(compute="B_fi_programa")
    fecha_termino_programa = fields.Date(compute="B_ff_programa")

    dias_transcurridos = fields.Integer(compute="DiasTrans")

    # MONTO PROGRAMADO PARA ESTA ESTIMACION
    monto_programado_est = fields.Float(digits=(12,2), compute="PenasConvencionales")
    # PORCENTAJE LLEVADO DE LA ESTIMACION, VER SI APLICAR REALMENTE, PUEDE SER UTIL
    porcentaje_est = fields.Float(compute="PenasConvencionales")
    # reduccion = fields.Float(compute="MontoProgramadoESt", string='Reduccion')

    montoreal = fields.Float(compute="MontoRealEst", string='MONTO EJECUTADO REAL PARA ESTA ESTIMACION')
    diasdif = fields.Integer(string='Dias de diferencia', compute="PenasConvencionales")
    dias_desfasamiento = fields.Float(string='DIAS DE DESFASAMIENTO', compute="PenasConvencionales")
    monto_atraso = fields.Float(string='MONTO DE ATRASO', digits=(12,2), compute="PenasConvencionales")
    diasperiodo = fields.Float(string='Dia total del periodo', compute="PenasConvencionales")
    diasest = fields.Float(string='', compute="PenasConvencionales")
    diastransest = fields.Float(string='', compute="PenasConvencionales")

    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
    total_ret_est = fields.Float(string='', digits=(12,2), compute="PenasConvencionales")
    # PORCENTAJE DE LA RETENCION TOTAL
    porc_total_ret = fields.Float(string='', compute="PenasConvencionales")
    # RETENIDO ANTERIORMENTE
    retenido_anteriormente = fields.Float(string='', compute='ret_anterior')
    # RETENCION NETA A APLICAR EN ESTA ESTIMACION
    ret_neta_est = fields.Float(string='',)
    # DEVOLUCION A EFECTUAR EN ESTA ESTIMACION
    devolucion_est = fields.Float(string='', compute='devolucion_est_metod')

    montodiario_programado = fields.Float(string='MONTO DIARIO PROGRAMADO', digits=(12,2), compute="PenasConvencionales")
    diasrealesrelacion = fields.Float(string='DIAS EJECUTADOS REALCES CON RELACION  AL MONTO DIARIO PROGRAMADO', digits=(12,2)
                                      , compute="PenasConvencionales")
    select = [('diario', 'Diario'),('mensual','Mensual'),('ninguno','Ninguno')]
    # CAMPOS RELACIONADOS DESDE CONTRATO PARA LA RETENCION
    periodicidadretencion = fields.Selection(select, string="Periodicidad Retención", related="obra.numero_contrato.periodicidadretencion")
    retencion = fields.Float(string="% Retención", related="obra.numero_contrato.retencion")

    _url = fields.Char(compute="_calc_url", string="Vista de impresión")

    xd = fields.Float(compute="computeSeccion")

    @api.multi
    def OrdenesPago(self):
        # VISTA OBJETIVO
        view = self.env.ref('ejecucion_obra.orden_cambio_form')
        # CONTADOR SI YA FUE CREADO
        count = self.env['control.ordenes_cambio'].search_count([('vinculo_estimaciones.id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['control.ordenes_cambio'].search([('vinculo_estimaciones.id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Ordenes de Cambio',
                'res_model': 'control.ordenes_cambio',
                'view_mode': 'form',
                'context': {'default_vinculo_estimaciones': self.id},
                'target': 'new',
                'view_id': view.id,
                'res_id': search.id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Ordenes de Cambio',
                'res_model': 'control.ordenes_cambio',
                'view_mode': 'form',
                'context': {'default_vinculo_estimaciones': self.id},
                'target': 'new',
                'view_id': view.id,
            }

    # MONTO REAL PARA ESTA ESTIMACION
    @api.one
    def MontoRealEst(self):
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        acum = 0
        for i in b_est:
            if i.idobra <= self.idobra:
                acum = acum + i.estimado
                self.montoreal = acum
            else:
                print('se paso de numero estimacion')

    # METODOS DE RESTRICCIONES DE FECHAS
    '''@api.multi
    @api.onchange('fecha_termino_estimacion', 'fecha_inicio_estimacion')
    def VerifFechaEst(self):
        if str(self.fecha_inicio_estimacion) > str(self.fecha_termino_estimacion):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la actual, '
                                     'por favor seleccione una fecha actual o posterior')
        else:
            return False

    @api.multi
    @api.onchange('fecha_presentacion', 'fecha_revision')
    def VerifFechaEst2(self):
        if str(self.fecha_revision) < str(self.fecha_presentacion):
            raise exceptions.Warning('No se puede seleccionar una Fecha anterior a la actual, '
                                     'por favor seleccione una fecha actual o posterior')
        else:
            return False

    @api.multi
    @api.onchange('fecha_termino_estimacion', 'fecha_inicio_estimacion')
    def ExcepcionFechaESt(self):
        f1 = datetime.strptime(str(self.fecha_inicio_estimacion), "%Y-%m-%d")
        f2 = datetime.strptime(str(self.fecha_termino_estimacion), "%Y-%m-%d")
        r = f2 - f1
        dias = r.days
        if dias > 31:
            raise exceptions.Warning('Los dias entre cada fecha exceden los 31 dias!!')
        else:
            print('si')'''

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

    # METODO PARA CALCULOS DE REPORTE DE PENAS CONVENCIONALES
    @api.one
    def PenasConvencionales(self):
        # FECHA INICIO ESTIMACION
        f_estimacion_inicio = self.fecha_inicio_estimacion
        # FECHA TERMINO ESTIMACION
        f_estimacion_termino = self.fecha_termino_estimacion
        # DIA DE TERMINO DE LA ESTIMACION
        f_est_termino_dia = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
        # BUSCAR FECHAS DEL PROGRAMA
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        acum = 0
        # FECHA INICIO DEL PROGRAMA
        fecha_inicio_programa = b_programa.fecha_inicio_programa
        # FECHA TERMINO PROGRAMA
        fecha_inicio_termino = b_programa.fecha_termino_programa

        monto_contrato = b_programa.total_partida
        # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
        diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
        acum = 0
        for i in b_programa.programa_contratos:
            fechatermino = i.fecha_termino
            # fechainicio = i.fecha_inicio
            # f_termino_dia = datetime.strptime(str(fechatermino), "%Y-%m-%d")
            date_format = "%Y-%m-%d"
            # fecha termino del programa, mes y año
            datem = datetime(fecha_inicio_termino.year, fecha_inicio_termino.month, 1)
            # fecha termino de la estimacion mes y año
            datem2 = datetime(f_estimacion_termino.year, f_estimacion_termino.month, 1)
            # ciclo de fecha termino del programa mes y año
            datem3 = datetime(fechatermino.year, fechatermino.month, 1)
            # fecha termino de estimacion mes y año
            datem4 = datetime(f_estimacion_termino.year, f_estimacion_termino.month, 1)

            print('inicio ciclo')
            # LAS FECHAS DE ESTIMACIONES SON EL MISMO DIA
            if f_estimacion_inicio == f_estimacion_termino:
                acum = acum + i.monto
                m_estimado = acum
                self.monto_programado_est = m_estimado
            # SI LA FECHA DEL TERMINO DE LA ESTIMACION ES IGUAL A LA DEL PROGRAMA HACER CALCULO FINAL
            elif datem == datem2:
                print('final')
                acum = acum + i.monto
                f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                r = f2 - f1
                dias = r.days
                f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                f4 = datetime.strptime(str(fecha_inicio_termino), date_format)
                r2 = f4 - f3
                total_dias_periodo = r2.days
                # ---------------------
                # fecha estimacion inicio, fecha desde del dia 1
                fei = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                # fecha termino programa
                ftp = datetime.strptime(str(fecha_inicio_termino), date_format)
                r3 = ftp - fei
                # Contar el numero dias del inicio de la estimacion hasta el dia del termino programa
                d_est_programatermino = r3.days
                # FECHA TERMINACION ESTIMACION
                fet = datetime.strptime(str(f_estimacion_termino), date_format)
                # FECHA TERMINO PROGRAMA
                ftp = datetime.strptime(str(fecha_inicio_termino), date_format)
                r4 = ftp - fet
                # Contar el numero de dias desde el termino de la estimacion hasta el termino del programa
                d_esttermino_programa = r4.days

                # -------------------------
                # ultimo monto programa entre dias hasta final programa por dias del final de estimacion
                # hasta final de programa
                ff = d_esttermino_programa
                ff2 = d_est_programatermino + 1
                # FORMULA: ULTIMO MONTO / DIA INICIO MES ESTIMACION HASTA DIA TERMINO PROGRAMA * DIA TERMINO ESTIMACION
                # HASTA DIA TERMINO PORGRAMA

                monto_final = (i.monto / ff2) * ff
                m_estimado = acum - monto_final

                # MONTO PROGRAMADO PARA ESTA ESTIMACION
                self.monto_programado_est = m_estimado
                # self.reduccion = monto_final
                # DIAS DE DIFERENCIA ENTRE EST
                self.diasdif = dias + 1
                # TOTAL DIAS PERIODO PROGRAMA
                self.diasperiodo = total_dias_periodo
                # MONTO DIARIO PROGRAMADO
                self.montodiario_programado = self.monto_programado_est / self.dias_transcurridos
                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                # DIAS DE DESFASAMIENTO
                if self.dias_transcurridos <= self.diasrealesrelacion:
                    self.dias_desfasamiento = 0
                else:
                    self.dias_desfasamiento = self.dias_transcurridos - self.diasrealesrelacion
                # MONTO DE ATRASO
                self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                # PORCENTAJE ESTIMADO
                self.porcentaje_est = (m_estimado / monto_contrato) * 100
                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                # %
                self.porc_total_ret = self.retencion * self.dias_desfasamiento
                self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
            # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
            elif f_est_termino_dia.day == diasest:
                # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                if datem3 > datem4:
                    print('se paso de fecha')
                # SI ES MENOR IGUAL CONTINUAR CICLO
                elif datem3 <= datem4:
                    acum = acum + i.monto
                    print('CUANDO LA ESTIMACION ES IGUAL AL DIA DEL ULTIMO MES')
                    print('---')
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    dias = r.days
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_inicio_termino), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days

                    # ---------------------
                    diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                    f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                    f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r4 = f8 - f7
                    diastransest = r4.days
                    # -------------------------
                    m_estimado = acum
                    self.diasest = diasest
                    self.diastransest = diastransest

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_est = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdif = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodo = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programado = self.monto_programado_est / self.dias_transcurridos
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridos <= self.diasrealesrelacion:
                        self.dias_desfasamiento = 0
                    else:
                        self.dias_desfasamiento = self.dias_transcurridos - self.diasrealesrelacion
                    # MONTO DE ATRASO
                    self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    # %
                    self.porc_total_ret = self.retencion * self.dias_desfasamiento
                    self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100

                else:
                    print('no')
            # SI EL TERMINO DE LA ESTIMACION ES MENOR AL DIA TOTAL DEL MES ENTONCES SE MODIFICARA EL MONTO ACUMULADO
            # CON UNA FORMULA PARA CALCULAR EL MONTO ACTUAL HASTA LA FECHA DE TERMINO DE LA ESTIMACION
            elif f_est_termino_dia.day < diasest:
                if datem3 > datem4:
                    print('se paso de fecha')
                elif f_estimacion_inicio.month is not f_estimacion_termino.month:
                    print('1')
                    acum = acum + i.monto
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    dias = r.days
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_inicio_termino), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days

                    # ---------------------
                    diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                    f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                    f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r4 = f8 - f7
                    diastransest = r4.days
                    # -------------------------
                    ultimo_monto = i.monto
                    x1 = acum - ultimo_monto
                    x2 = i.monto / diasest
                    m_estimado = x1 + x2 * (diastransest + 1)

                    self.diasest = diasest
                    self.diastransest = diastransest

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_est = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdif = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodo = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programado = self.monto_programado_est / self.dias_transcurridos
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridos <= self.diasrealesrelacion:
                        self.dias_desfasamiento = 0
                    else:
                        self.dias_desfasamiento = self.dias_transcurridos - self.diasrealesrelacion
                    # MONTO DE ATRASO
                    self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    # %
                    self.porc_total_ret = self.retencion * self.dias_desfasamiento
                    self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                elif datem3 <= datem4:
                    acum = acum + i.monto
                    print('CUANDO LA ESTIMACION ES MENOS DE 30 DIAS EN EL MES')
                    print('---')
                    # acum += i.monto
                    print(acum)
                    print('....')
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    dias = r.days
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_inicio_termino), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days

                    # ---------------------
                    diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                    f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                    f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r4 = f8 - f7
                    diastransest = r4.days
                    # -------------------------
                    # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                    monto_est_dias = (i.monto / diasest)
                    m_estimado = acum - monto_est_dias
                    self.diasest = diasest
                    self.diastransest = diastransest

                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.monto_programado_est = m_estimado
                    # self.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    self.diasdif = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    self.diasperiodo = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO
                    self.montodiario_programado = self.monto_programado_est / self.dias_transcurridos
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                    # DIAS DE DESFASAMIENTO
                    if self.dias_transcurridos <= self.diasrealesrelacion:
                        self.dias_desfasamiento = 0
                    else:
                        self.dias_desfasamiento = self.dias_transcurridos - self.diasrealesrelacion
                    # MONTO DE ATRASO
                    self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    # %
                    self.porc_total_ret = self.retencion * self.dias_desfasamiento
                    self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                else:
                    print('no x2')
            else:
                print('se termino el cliclo')

    # METODO RETENIDO ANTERIORMENTE
    @api.one
    @api.depends('total_ret_est')
    def ret_anterior(self):
        b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        # print(b_est[int(self.idobra)-1].total_ret_est)
        if b_est_count == 0:
            print('AUN NO HAY ESTIMACIONES')
        else:
            if b_est[int(self.idobra)-1].idobra == b_est[0].idobra:
                self.retenido_anteriormente = 0
            else:
                self.retenido_anteriormente = b_est[int(self.idobra)-2].total_ret_est

    # RETENCION NETA A APLICAR EN ESTA ESTIMACION
    @api.multi
    @api.onchange('retenido_anteriormente')
    def ret_neta_est_metod(self):
        if self.total_ret_est > self.retenido_anteriormente:
            self.ret_neta_est = self.total_ret_est - self.retenido_anteriormente
        else:
            self.ret_neta_est = 0

    # DEVOLUCION NETA A APLICAR EN ESTA ESTIMACION
    @api.one
    @api.depends('retenido_anteriormente')
    def devolucion_est_metod(self):
        if self.total_ret_est < self.retenido_anteriormente:
            self.devolucion_est = self.retenido_anteriormente - self.total_ret_est
        else:
            self.devolucion_est = 0

    # DIAS TRANSCURRIDOS DESDE INICIO DE PROGRAMA HASTA TERMINO DE ESTIMACION
    @api.one
    def DiasTrans(self):
        fe1 = self.fecha_inicio_programa
        fe2 = self.fecha_termino_estimacion
        date_format = "%Y-%m-%d"
        f1 = datetime.strptime(str(fe1), date_format)
        f2 = datetime.strptime(str(fe2), date_format)
        r = f2 - f1
        self.dias_transcurridos = r.days + 1

    # FECHA INICIO PROGRAMA
    @api.one
    def B_fi_programa(self):
        b_fecha = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        self.fecha_inicio_programa = str(b_fecha.fecha_inicio_programa)

    # FECHA TERMINO PROGRAMA
    @api.one
    def B_ff_programa(self):
        b_fecha = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        self.fecha_termino_programa = str(b_fecha.fecha_termino_programa)

    # METODO BUSCAR DIRECTOR DE OBRAS CONFIGURACION
    @api.one
    def BuscarDirector(self):
        b_director = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_subdirector_obra')
        self.subdirector_contrato = b_director

    # ID DE LA ESTIMACION
    @api.one
    def estid(self):
        numero = 100000 + self.id
        self.ide_estimacion = str(numero)

    # COMPUTE CONTAR ESTIMACIONES
    '''@api.one
    @api.depends('obra')
    def ido(self):
        self.idobra = str(self.env['control.estimaciones'].search_count([('obra', '=', self.obra.id)]))'''

    # METODO BUSCAR IVA EN CONFIGURACION
    @api.one
    def BuscarIva(self):
        iva = self.env['ir.config_parameter'].sudo().get_param('generales.iva')
        self.b_iva = iva

    # NUMERO ESTIMACION
    @api.model
    def create(self, values):
        num = int(values['estimacion_ids'])
        num = num + 1
        values['idobra'] = str(num)
        return super(Estimaciones, self).create(values)

    '''# METODO PARA EL CONTADOR DE ESTIMACIONES
    @api.model
    def create(self, values):
        count = self.env['partidas.partidas'].search_count([('id', '=', self.obra.id)])
        print(count)
        count = count + 1
        values['numero_estimacion'] = count
        return super(Estimaciones, self).create(values)'''

    # METODO CREATE PARA CREAR LA ID DE ESTIMACION
    @api.multi
    @api.onchange('obra')
    def IdEstimacion(self):
        self.estimacion_ids = str(self.env['control.estimaciones'].search_count([('obra', '=', self.obra.id)]))

    # METODO PARA JALAR DATOS DE LAS DEDUCCIONES DEL CONTRATO
    @api.multi
    @api.onchange('conceptos_partidas')  # if these fields are changed, call method
    def deduccion(self):
        b_deducciones = self.env['proceso.elaboracion_contrato'].browse(self.numero_contrato.id)

        self.update({
            'deducciones': [[5]]
        })

        for deducciones in b_deducciones.deducciones:
            self.update({
                'deducciones': [[0, 0, {'name': deducciones.name, 'porcentaje': deducciones.porcentaje}]]
            })

    # METODO PARA JALAR IMPORTE DE LOS CONCEPTOS DE PARTIDA
    @api.onchange('conceptos_partidas')
    def suma_conceptos(self):
        suma = 0
        for i in self.conceptos_partidas:
            resultado = i.importe_ejecutado
            suma = suma + resultado
            self.estimado = suma

    # METODO PARA CALCULAR ESTIMACION NETA SIN IVA
    @api.one
    @api.depends('estimado', 'sub_total_esc_h')
    def Estimacion_sinIva(self):
        if self.sub_total_esc_h > 0:
            self.estimacion_subtotal = self.sub_total_esc_h
        else:
            for rec in self:
                rec.update({
                    'estimacion_subtotal': self.estimado - self.amort_anticipo
                }) # (self.estimado - self.amort_anticipo) - (self.estimado * self.b_iva)

    # METODO PARA CALCULAR ESTIMACION IVA.
    @api.one
    @api.depends('estimado')
    def Estimacion_Iva(self):
        for rec in self:
            rec.update({
                'estimacion_iva': (self.estimado - self.amort_anticipo) * self.b_iva
            })

    # IMPORTE LIQUIDO
    @api.one
    @api.depends('estimado_deducciones')
    def Importe_liquido(self):
        for rec in self:
            rec.update({
                'a_pagar': self.estimacion_facturado - self.estimado_deducciones
            })

    # METODO PARA CALCULAR ESTIMACION + IVA
    @api.one
    @api.depends('estimacion_iva')
    def Estimacion_conIva(self):
        for rec in self:
            rec.update({
                'estimacion_facturado': self.estimacion_subtotal + self.estimacion_iva
            })

    # METODO PARA SUMAR DEDUCCIONES
    @api.multi
    @api.onchange('estimacion_facturado')
    def SumaDeducciones(self):
        suma = 0
        for i in self.deducciones:
            resultado = i.valor
            suma = suma + resultado
            self.estimado_deducciones = suma

    # METODO PARA CALCULAR AMORTIZACION 30%
    @api.one
    @api.depends('estimado', 'sub_total_esc_h')
    def amortizacion_anticipo(self):
        if self.sub_total_esc_h > 0:
            self.amort_anticipo = 0
        else:
            for rec in self:
                rec.update({
                    'amort_anticipo': self.estimado * self.amort_anticipo_partida
                })

    # METODO PARA AGREGAR IMPORTE A DEDUCCIONES
    @api.multi
    @api.onchange('estimado')
    def deduc(self):
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })

    # METODO PARA INSERTAR CONCEPTOS CONTRATADOS     ---------------VERIFICAR COMO CORRER EL METODO AL ENTRAR
    @api.multi
    @api.depends('p_id')
    def conceptosEjecutados(self):
        adirecta_id = self.env['partidas.partidas'].browse(self.obra.id)
        self.update({
            'conceptos_partidas': [[5]]
        })
        for conceptos in adirecta_id.conceptos_partidas:
            self.update({
                'conceptos_partidas': [[0, 0, {'id_partida': conceptos.id_partida, 'categoria': conceptos.categoria,
                                               'clave_linea': conceptos.clave_linea, 'concepto': conceptos.concepto,
                                               'medida': conceptos.medida,
                                               'precio_unitario': conceptos.precio_unitario,
                                               'cantidad': conceptos.cantidad}]]
            })


    @api.one
    def Estimacion(self):
        self.estimacion_id = self.id

    @api.one
    def obra_enlace(self):
        self.obra_id = self.obra


class Deducciones(models.Model):
    _name = 'control.deducciones'

    name = fields.Char()
    porcentaje = fields.Float()
    valor = fields.Float()


class Ordenes_Cambio(models.Model):
    _name = 'control.ordenes_cambio'
    _rec_name = 'vinculo_estimaciones'
    orden_pago = fields.Char(string='Orden de pago',required=True, size=10)
    vinculo_estimaciones = fields.Many2one('control.estimaciones', string='Estimación id', store=True)
    numero_contrato = fields.Many2one('proceso.elaboracion_contrato', string='Contrato',
                                      related="vinculo_estimaciones.obra.numero_contrato")

    fecha = fields.Date(string='Fecha',required=True)
    total_estimado = fields.Float(string='Total estimación',required=True)
    cuentas_bancos = fields.Many2one('control.cuentasbancos',required=True)

    @api.constrains('orden_pago')
    def _validar_lenorderpago(self):
        if len(str(self.orden_pago)) < 10:
            raise ValidationError("La orden de pago debe de ser de 10 digitos.")

class CuentasBanco(models.Model):
    _name = 'control.cuentasbancos'
    name = fields.Char()