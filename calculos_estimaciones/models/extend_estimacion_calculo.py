from odoo import models, fields, api, exceptions
from datetime import date
from datetime import datetime
import calendar
import warnings


class EstimacionesCalculos(models.Model):
    _inherit = 'control.estimaciones'

    conceptos_partidas2 = fields.Many2many('control.detalle_conceptos', compute="conceptos_qweb_conceptos")  # compute="conceptosEjecutados"

    @api.one
    def conceptos_qweb_conceptos(self):
        estimacion = self.env['control.estimaciones']
        anexos = self.env['control.detalle_conceptos'].search([('id_partida', '=', self.obra.id),
                                                               ('num_est', '=', int(self.idobra)), ('importe_ejecutado', '!=', 0.0)])
        for i in sorted(anexos, reverse=True):
            datos= {
                'conceptos_partidas2': [[4, i.id, {}
                ]]
                }

            x = estimacion.browse(self.id)
            tabla = x.update(datos)
    
    @api.multi
    @api.onchange('p_id')
    def fechaAnterior(self):
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        c_est = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        ultima_fecha_inicio = ""
        ultima_fecha_termino = ""
        if c_est == 0:
            pass
        else:
            fecha_inicio_estimacion = b_est[int(c_est) - 1].fecha_termino_estimacion

            dia_ultimo_mes = calendar.monthrange(fecha_inicio_estimacion.year, fecha_inicio_estimacion.month)[1]
            fechax_ = str(fecha_inicio_estimacion)
            ff = str(fechax_[8] + fechax_[9])
            ff_int = int(ff)
            if int(dia_ultimo_mes) == int(ff_int):
                print(fecha_inicio_estimacion, 'yyyyyyyyyyyyy')
                fff = str(fechax_[5] + fechax_[6])
                dd = int(fff) + 1

                anio = str(fechax_[2] + fechax_[3])

                if len(str(dd)) >= 2:
                    dds = str(dd)
                else:
                    dds = '0' + str(dd)

                if dd == 13:
                    dds = '01'
                    aniox = int(anio) + 1
                    anio = str(aniox)

                mm = '01'
                fechay_ = fechax_[0] + fechax_[1] + anio[0] + anio[1] + fechax_[
                    4] + dds[0] + dds[1] + fechax_[7] + mm[0] + mm[1]

                ultima_fecha_inicio = fechay_

                fechay_x = datetime.strptime(str(ultima_fecha_inicio), '%Y-%m-%d')

                dia_ultimo_mes = calendar.monthrange(fechay_x.year, fechay_x.month)[1]
                dia = str(dia_ultimo_mes)
                fecha_final_ = str(fechay_x)

                fecha_final = fecha_final_[0] + fecha_final_[1] + fecha_final_[2] + fecha_final_[3] + fecha_final_[
                    4] + fecha_final_[5] + fecha_final_[6] + fecha_final_[7] + dia[0] + dia[1]

                ultima_fecha_termino = fecha_final

            else:
                fecha_i_ = str(fecha_inicio_estimacion)

                dia_s = str(fecha_i_[8] + fecha_i_[9])

                dias_sint = int(dia_s) + 1
                if len(str(dias_sint)) >= 2:
                    dias_str = str(dias_sint)
                else:
                    dias_str = '0' + str(dias_sint)

                fecha_i = fecha_i_[0] + fecha_i_[1] + fecha_i_[2] + fecha_i_[3] + fecha_i_[4] + fecha_i_[5] + \
                          fecha_i_[6] + fecha_i_[7] + dias_str[0] + dias_str[1]

                ultima_fecha_inicio = fecha_i

                dia = str(dia_ultimo_mes)
                fecha_final_ = str(ultima_fecha_inicio)

                fecha_final = fecha_final_[0] + fecha_final_[1] + fecha_final_[2] + fecha_final_[3] + fecha_final_[
                    4] + fecha_final_[5] + fecha_final_[6] + fecha_final_[7] + dia[0] + dia[1]
                ultima_fecha_termino = fecha_final

            self.fecha_inicio_estimacion = ultima_fecha_inicio
            self.fecha_termino_estimacion = ultima_fecha_termino

    # METODO PARA CALCULOS DE REPORTE DE PENAS CONVENCIONALES
    @api.multi
    @api.onchange('conceptos_partidas', 'amort_anticipo_partida', 'si_aplica_estimacion', 'si_aplica_amortizar')
    def penas_convencionales_metodox(self):
        b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        num_est = 0
        if not self.idobra:
            num_est = b_est_count + 1
        else:
            num_est = int(self.idobra)

        
        b_est = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
        # ACUMULAMOS RETENIDOS ANTERIORES
        acum_Ret = 0
        for i in b_est:
            if not self.idobra:
                if not i.idobra:
                    break
                else:
                    acum_Ret += i.ret_neta_est
            else:
                if int(self.idobra) <= int(i.idobra):
                    pass
                else:
                    acum_Ret += i.ret_neta_est
        # SACAMOS EL TOTAL ESTIMADO DE LOS CONCEPTOS
        suma = 0
        for i in self.conceptos_partidas:
            resultado = i.importe_ejecutado
            suma = suma + resultado
        # ESCALATORIA
        if self.tipo_estimacion == '2' or self.tipo_estimacion == '3':
            self.estimado = self.sub_total_esc_h
            suma = self.sub_total_esc_h
        else:
            self.estimado = suma
        # MONTO ACTUAL A EJECUTAR ESTIMADO
        if b_est_count == 0:
            if not self.idobra:
                self.montoreal = suma
        else:
            acum_real = 0
            for i in b_est:
                if not self.idobra:
                    acum_real += + i.estimado
                    self.montoreal = acum_real + self.estimado
                elif int(self.idobra) == 1:
                    print('xdxs-------------dxd')
                    '''if b_est_count > 1:
                        acum_real += i.estimado
                        self.montoreal = acum_real + self.estimado
                    else:'''
                    acum_real += i.estimado
                    self.montoreal = self.estimado
                elif int(i.idobra) < int(self.idobra):
                    print('AQUI')
                    acum_real += i.estimado
                    self.montoreal = acum_real + self.estimado

        # RETENIDO ANTERIORMENTE
        self.retenido_anteriormente = acum_Ret
        if int(b_est_count) == 0 or int(self.idobra) == 1:
            self.retenido_anteriormente = 0
        self.nuevo_metodo = True  # INDICA SI ES NUEVA ESTIMACION, NO IMPORTADA DE SIDEOP PARA CONDICION DE QWEB
        f_estimacion_inicio = self.fecha_inicio_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
        f_estimacion_termino = self.fecha_termino_estimacion  # FECHA INICIO Y TERMINO ESTIMACION
        f_est_termino_dia = datetime.strptime(str(f_estimacion_termino),
                                                "%Y-%m-%d")  # DIA DE TERMINO DE LA ESTIMACION
        # BUSCAR FECHAS DEL PROGRAMA
        b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        # VERIFICAR SI EXISTE CONVENIO
        _search_cove = self.env['proceso.convenios_modificado'].search_count(
            [("nombre_contrato", "=", self.obra.nombre_contrato),
                ("tipo_convenio", "=", 'PL' or 'BOTH')])
        b_convenio = self.env['proceso.convenios_modificado'].search(
            [('nombre_contrato', '=', self.obra.nombre_contrato)])
        if _search_cove > 0:
            for i in b_convenio:
                if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                    fecha_prog = datetime.strptime(str(i.plazo_fecha_inicio), "%Y-%m-%d").date()
                    fecha_inicio_programa = fecha_prog
                    fecha_prog2 = datetime.strptime(str(i.plazo_fecha_termino), "%Y-%m-%d").date()
                    fecha_termino_programa = fecha_prog2
        else:
            # FECHA INICIO Y TERMINO DEL PROGRAMA
            fecha_inicio_programa = b_programa.fecha_inicio_programa
            fecha_termino_programa = b_programa.fecha_termino_programa

        # DIAS TRANSCURRIDOS DESDE EL INICIO DEL CONTRATO
        if fecha_inicio_programa and fecha_termino_programa:
            f1h = datetime.strptime(str(fecha_inicio_programa), "%Y-%m-%d")
            f2h = datetime.strptime(str(fecha_termino_programa), "%Y-%m-%d")
            rh = f2h - f1h
            self.dias_transcurridos = rh.days + 1

        # CALCULO DEL A_FIN
        total_programa = 0
        for i in b_programa:
            total_programa = i.total_programa
        acum_afin_calculo = 0
        est_actual = 0
        for x in b_est:
            if not self.idobra or self.idobra == "":
                est_actual = b_est_count + 1
            else:
                est_actual = b_est_count
            if int(x.idobra) >= est_actual:
                pass
            else:
                acum_afin_calculo += x.estimado
        self.a_fin = ((acum_afin_calculo + self.estimado) / total_programa) * 100
        # TERMINA A_FIN

        monto_contrato = b_programa.total_programa
        # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
        diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
        self.diasest = diasest
        acum = 0
        cont = 0
        date_format = "%Y-%m-%d"
        # CICLO QUE RECORRE LA LISTA DE PROGRAMAS
        for i in sorted(b_programa.programa_contratos):
            cont = cont + 1
            fechatermino = i.fecha_termino
            fechainicio = i.fecha_inicio
            date_format = "%Y-%m-%d"
            # INDICAR SI ES UN PROGRAMA QUE ABARCA VARIOS MESES
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
            fecha_terminoest_todo = datetime(f_estimacion_termino.year, f_estimacion_termino.month,
                                                f_estimacion_termino.day)
            # fecha termino de estimacion mes y año
            print('CON LA ESTIMACION #', self.idobra, ' +++++')
            print('INICIA EL CICLO ******', cont)
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
                monto_final = 0
                b_programa_c = self.env['proceso.programa'].search_count([('obra.id', '=', self.obra.id)])
                if b_programa_c == 1:  # print('solo hay un monto')
                    # monto_final = (i.monto / (dias + 1)) * ff
                    m_estimado = m_estimado = (i.monto / (total_dias_periodo + 1)) * (dias_trans_mesactual + 1)
                elif self.idobra == 1 or b_est_count == 0:
                    monto_final = 0
                    m_estimado = (acum - i.monto) + monto_final
                else:
                    # monto_final = (i.monto / (dias + 1)) * ff
                    monto_final = (i.monto / (dia_inicio_atermino + 1)) * (dias_trans_mesactual + 1)
                    m_estimado = (acum - i.monto) + monto_final

                if fechatermino < f_estimacion_termino:
                    m_estimado = acum

                self.ultimomonto = monto_final
                self.diasest = diasest
                self.diastransest = ff2
                # MONTO PROGRAMADO PARA ESTA ESTIMACION
                self.monto_programado_est = m_estimado
                # self.reduccion = monto_final
                # DIAS DE DIFERENCIA ENTRE EST
                self.diasdif = dias + 1
                # TOTAL DIAS PERIODO PROGRAMA
                self.diasperiodo = total_dias_periodo
                # MONTO DIARIO PROGRAMADO
                self.montodiario_programado = self.monto_programado_est / self.diasdif
                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                if self.montodiario_programado == 0:
                    self.montodiario_programado = 1
                self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                    self.dias_desfasamiento = 0
                else:
                    self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion
                # MONTO DE ATRASO
                self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                # PORCENTAJE ESTIMADO
                self.porcentaje_est = (m_estimado / monto_contrato) * 100
                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                self.porc_total_ret = self.retencion * self.dias_desfasamiento
                self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                if self.retenido_anteriormente == 0:  # RETENCION
                    if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                        self.ret_neta_est = 0
                        self.devolucion_est = 0
                    else:
                        self.ret_neta_est = self.total_ret_est * -1
                        self.devolucion_est = 0
                elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                    self.ret_neta_est = self.retenido_anteriormente * -1
                    self.devolucion_est = self.retenido_anteriormente * -1
                elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                    self.ret_neta_est = 0
                    self.devolucion_est = 0
                elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                    self.devolucion_est = 0
                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                    self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est

            # SI EL PROGRAMA ES UNICO Y DE VARIOS MESES
            elif int(num_months) > 2:
                print(' FUERA DE MES', num_months)
                acum = acum + i.monto
                # dias transcurridos
                f_termino_esti = datetime.strptime(str(f_estimacion_termino), date_format)
                f_inicio_prog = datetime.strptime(str(fecha_inicio_programa), date_format)
                r_diastrans = f_termino_esti - f_inicio_prog
                dias_trans = r_diastrans.days + 1
                m_estimado = (acum / fuera_mes) * dias_trans
                self.diastransest = dias_trans

                if fechatermino < f_estimacion_termino:
                    m_estimado = acum

                # MONTO PROGRAMADO PARA ESTA ESTIMACION
                self.monto_programado_est = m_estimado
                f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                r = f2 - f1
                # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                # TERMINO DE LA ESTIMACION
                dias = r.days + 1
                self.diasdif = dias

                f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                r2 = f4 - f3
                # DIAS DEL PERIODO
                total_dias_periodo = r2.days
                self.diasperiodo = total_dias_periodo

                # MONTO DIARIO PROGRAMADO
                self.montodiario_programado = self.monto_programado_est / self.diasdif
                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                    self.dias_desfasamiento = 0
                else:
                    self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion
                # MONTO DE ATRASO
                self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado
                # PORCENTAJE ESTIMADO
                self.porcentaje_est = (m_estimado / monto_contrato) * 100
                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                self.porc_total_ret = self.retencion * self.dias_desfasamiento
                self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                if self.retenido_anteriormente == 0:  # RETENCION
                    if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                        self.ret_neta_est = 0
                        self.devolucion_est = 0
                    else:
                        self.ret_neta_est = self.total_ret_est * -1
                        self.devolucion_est = 0
                elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                    self.ret_neta_est = self.retenido_anteriormente * -1
                    self.devolucion_est = self.retenido_anteriormente * -1
                elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                    self.ret_neta_est = 0
                    self.devolucion_est = 0
                elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                    self.devolucion_est = 0
                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                    self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est

            # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
            elif f_est_termino_dia.day == diasest:
                # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                if fechatermino <= self.fecha_termino_estimacion:
                    acum = acum + i.monto
                    print('CUANDO LA ESTIMACION ES IGUAL AL DIA DEL ULTIMO MES')
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    dias = r.days  # DIAS DE DIFERENCIA ENTRE EST
                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    total_dias_periodo = r2.days  # TOTAL DIAS PERIODO PROGRAMA
                    diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
                    f7 = datetime.strptime(str(f_estimacion_termino.replace(day=1)), date_format)
                    f8 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r4 = f8 - f7
                    diastransest = r4.days
                    m_estimado = acum
                    self.diasest = diasest
                    self.diastransest = diastransest
                    self.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.diasdif = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                    self.diasperiodo = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                    self.montodiario_programado = self.monto_programado_est / self.diasdif  # MONTO DIARIO PROGRAMADO
                    if self.montodiario_programado == 0:  # DIAS EJECUTADOS REALES
                        self.montodiario_programado = 1  # CON RELACION AL
                    self.diasrealesrelacion = self.montoreal / self.montodiario_programado  # MONTO DIARIO PROGRAMADO
                    if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                        self.dias_desfasamiento = 0
                    else:
                        self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion

                    self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado  # MONTO DE ATRASO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                    self.porc_total_ret = self.retencion * self.dias_desfasamiento  # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100

                    if self.retenido_anteriormente == 0:  # RETENCION
                        if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                            self.ret_neta_est = 0
                            self.devolucion_est = 0
                        else:
                            self.ret_neta_est = self.total_ret_est * -1
                            self.devolucion_est = 0
                    elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                        self.ret_neta_est = self.retenido_anteriormente * -1
                        self.devolucion_est = self.retenido_anteriormente * -1
                    elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                        self.ret_neta_est = 0
                        self.devolucion_est = 0
                    elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                        self.devolucion_est = 0
                        self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                    elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                        self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                        self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                else:
                    print('FUERA DE FECHA')
            # SI EL TERMINO DE LA ESTIMACION ES MENOR AL DIA TOTAL DEL MES ENTONCES SE MODIFICARA EL MONTO ACUMULADO
            # CON UNA FORMULA PARA CALCULAR EL MONTO ACTUAL HASTA LA FECHA DE TERMINO DE LA ESTIMACION
            elif f_est_termino_dia.day < diasest:
                if f_termino_proglista > fecha_terminoest_y_m:
                    print('se paso de fecha 2')
                # SON MESES DIFERENTES
                elif f_estimacion_inicio.month is not f_estimacion_termino.month:
                    print('#1 EL MES FECHA EST INICIO ES DIFERENTE AL MES EST TERMINO')
                    esti = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id)])
                    if fecha_terminoest_y_m == fecha_terminop_y_m:
                        for x in esti:
                            if int(x.idobra) > int(self.idobra) or int(x.idobra) > (b_est_count + 1):
                                # SI NO ES LA ULTIMA ESTIMACION ENTONCES
                                pass
                            elif x.idobra == self.idobra or int(x.idobra) == (b_est_count + 1):
                                print('#2 COINCIDE CON EL ULTIMO MES DEL PROGRAMA CUANDO SON MESES DIFERENTES')
                                diasestx = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                    1]
                                fx = datetime.strptime(str(f_estimacion_inicio), date_format)
                                fy = datetime.strptime(str(f_estimacion_termino), date_format)
                                rx = fy - fx
                                diastransestx = rx.days  # DIAS TRANSCURRIDOS DE LA ESTIMACION
                                ultimo_monto = i.monto  # MONTO CORRESPONDIENTE A LA FECHA DE ESTIMACION CON LA DEL PROGRAMA
                                x1 = acum - ultimo_monto
                                x2 = i.monto / diasestx
                                m_estimado = x1 + x2 * (diastransestx + 1)

                                if fechatermino < f_estimacion_termino:
                                    m_estimado = acum

                                self.diasest = diasestx
                                self.diastransest = diastransestx
                                self.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                r = f2 - f1
                                dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE
                                self.diasdif = dias  # HASTA EL TERMINO DE LA ESTIMACION
                                f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                                r2 = f4 - f3
                                total_dias_periodo = r2.days
                                self.diasperiodo = total_dias_periodo  # DIAS DEL PERIODO
                                self.montodiario_programado = self.monto_programado_est / self.diasdif  # MONTO DIARIO PROGRAMADO
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                                if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                    self.dias_desfasamiento = 0
                                else:
                                    self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion
                                self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado  # MONTO DE ATRASO
                                self.porcentaje_est = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                self.porc_total_ret = self.retencion * self.dias_desfasamiento
                                self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                                if self.retenido_anteriormente == 0:  # RETENCION
                                    if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                                        self.ret_neta_est = 0
                                        self.devolucion_est = 0
                                    else:
                                        self.ret_neta_est = self.total_ret_est * -1
                                        self.devolucion_est = 0
                                elif (
                                        self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                                    self.ret_neta_est = self.retenido_anteriormente * -1
                                    self.devolucion_est = self.retenido_anteriormente * -1
                                elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                                    self.ret_neta_est = 0
                                    self.devolucion_est = 0
                                elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                                    self.devolucion_est = 0
                                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                                elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                                    self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                                    self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                        print('prosigue')
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
                            u_m = 0
                            fecha_inicio_aux = ''
                            fecha_termino_aux = ''
                            for c in b_programa.programa_contratos:
                                dat3 = datetime(c.fecha_termino.year,
                                                c.fecha_termino.month,
                                                c.fecha_termino.day)
                                if dat == dat3:
                                    print('fin')
                                elif dat3 > dat:
                                    print('terminar')
                                elif dat3 <= dat:
                                    acum_ftemtp += c.monto
                                    print('acumular')
                                    cx += 1
                                    u_m = c.monto
                                    fecha_inicio_aux = c.fecha_inicio
                                    fecha_termino_aux = c.fecha_termino
                                '''elif dat4 > f_sansion:
                                    print('SANSION TERMINAR')'''

                            ultimo_monto = u_m  # b_programa.programa_contratos[int(cx)].monto

                            f_pt = datetime.strptime(str(fecha_inicio_aux), date_format)
                            f_et = datetime.strptime(str(f_estimacion_termino), date_format)
                            ry = f_et - f_pt
                            d_entre_fecha = ry.days

                            ff_inicio = datetime.strptime(str(fecha_inicio_aux),
                                                            date_format)
                            ff_termino = datetime.strptime(str(fecha_termino_aux), date_format)
                            rf = ff_termino - ff_inicio
                            diastransestx = rf.days + 1
                            formula = (ultimo_monto / diastransestx) * (d_entre_fecha + 1)
                            acumulado = acum_ftemtp
                            if fechatermino < f_estimacion_termino:
                                m_estimado = acumulado
                            else:
                                m_estimado = acumulado + formula

                            self.ultimomonto = ultimo_monto
                            self.diasest = diasest
                            self.diastransest = diastransestx
                            self.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                            self.diasdif = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                            self.diasperiodo = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                            self.montodiario_programado = self.monto_programado_est / self.diasdif  # MONTO DIARIO PROGRAMADO
                            if self.montodiario_programado == 0:
                                self.montodiario_programado = 1
                            # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                            self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                            if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                self.dias_desfasamiento = 0
                            else:
                                self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion
                            self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado  # MONTO DE ATRASO
                            self.porcentaje_est = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                            # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                            self.porc_total_ret = self.retencion * self.dias_desfasamiento
                            self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                            if self.retenido_anteriormente == 0:  # RETENCION
                                if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                                    self.ret_neta_est = 0
                                    self.devolucion_est = 0
                                else:
                                    self.ret_neta_est = self.total_ret_est * -1
                                    self.devolucion_est = 0
                            elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                                self.ret_neta_est = self.retenido_anteriormente * -1
                                self.devolucion_est = self.retenido_anteriormente * -1
                            elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                                self.ret_neta_est = 0
                                self.devolucion_est = 0
                            elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                                self.devolucion_est = 0
                                self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                            elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                                self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                                self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                                # return acumulado
                        # SI LA FECHA DE TERMINO DE LA ESTIMACION ES MENOR A LA FECHA DEL TERMINO DEL PROGRAMA
                        elif dat < dat2:
                            print('#5 ES NORMAL')
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
                            # formula = (i.monto / dia_mes_termino) * (dia_mes_termino - diastransest) # cambio el 09/04/20
                            formula = (i.monto / dia_mes_termino) * diastransest  # SIDUR-ED-19-078.1698
                            if _programa_cx == 1:
                                m_estimado = x1 - formula
                            else:
                                m_estimado = x1 + formula

                            if fechatermino < f_estimacion_termino:
                                m_estimado = acum

                            self.ultimomonto = ultimo_monto
                            self.diasest = diasest
                            self.diastransest = diastransest
                            self.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                            self.diasdif = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                            self.diasperiodo = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                            self.montodiario_programado = self.monto_programado_est / self.diasdif  # MONTO DIARIO PROGRAMADO
                            if self.montodiario_programado == 0:
                                self.montodiario_programado = 1
                            # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                            self.diasrealesrelacion = self.montoreal / self.montodiario_programado

                            if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                                self.dias_desfasamiento = 0
                            else:
                                self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion
                            self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado  # MONTO DE ATRASO
                            self.porcentaje_est = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                            # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                            self.porc_total_ret = self.retencion * self.dias_desfasamiento
                            self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                            if self.retenido_anteriormente == 0:  # RETENCION
                                if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                                    self.ret_neta_est = 0
                                    self.devolucion_est = 0
                                else:
                                    self.ret_neta_est = self.total_ret_est * -1
                                    self.devolucion_est = 0
                            elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                                self.ret_neta_est = self.retenido_anteriormente * -1
                                self.devolucion_est = self.retenido_anteriormente * -1
                            elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                                self.ret_neta_est = 0
                                self.devolucion_est = 0
                            elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                                self.devolucion_est = 0
                                self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                            elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                                self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                                self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est

                                # elif f_termino_proglista <= fecha_terminoest_y_m:
                elif f_termino_prog_todo <= fecha_terminoest_todo:
                    acum = acum + i.monto
                    print('CUANDO LA ESTIMACION ES MENOS DE 30 DIAS EN EL MES')
                    f1 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO
                    dia_0 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                    dia_02 = datetime.strptime(str(f_estimacion_inicio), date_format)
                    dia_r = dia_02 - dia_0
                    dia_rr = dia_r.days  # dia 0 del mes al dia de inicio de esti
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
                    # DIAS RESTANTES PARA QUE ACABE EL MES
                    fr1 = datetime.strptime(str(f_estimacion_inicio), date_format)
                    fr2 = datetime.strptime(str(fechatermino), date_format)
                    rfr1 = fr2 - fr1
                    dias_restantes_terminomes = rfr1.days + 1

                    # -------------------------
                    # MONTO DE ESTA ESTIMACION ENTRE EL NUMERO DE DIAS QUE DURA LA ESTIMACION
                    if fechatermino < f_estimacion_termino:
                        formula = 1  # evitar errores
                    else:
                        if diastransest == diasest:
                            print(' termina en el dia ultimo del mes', diastransest, diasest)
                            # MONTO / DIAS DEL MES * NUMERO DE DIAS TRANSCURRIDOS DEL INICIO DEL MES DE LA EST AL TERMINO
                            formula = (i.monto / diasest) * diastransest
                        elif dia_progy < diasest:
                            # dia_progy = Dias desde el inicio de la fecha del programa hasta el termino
                            # diasest = Dias que tiene el mes de termino de est
                            print(' TERMINO PROG ES ANTES DEL MES')
                            formula = (i.monto / dia_progy) * diasx  # SIDUR-PF-18-220.1497
                        elif dia_progy == diasest:
                            formula = (i.monto / dias_restantes_terminomes) * diasx
                        else:
                            # normal
                            print(' termina antes', diastransest, diasest)
                            # formula = (i.monto / (diasest - dia_rr)) * diasx
                            # formula = (i.monto / diasest) * diasx
                            formula = (i.monto / diasest) * dias  # SIDUR-ED-20-002.1873

                    self.ultimomonto = i.monto
                    if str(self.idobra) == '1' or int(b_est_count) == 0:
                        m_estimado = formula
                    else:
                        m_estimado = (acum - i.monto) + formula  # (i.monto - formula)

                    if fechatermino < f_estimacion_termino:
                        m_estimado = acum

                    self.diasest = diasest
                    self.diastransest = diastransest + 1
                    fv = datetime.strptime(str(fecha_inicio_programa), date_format)
                    fvv = datetime.strptime(str(f_estimacion_termino), date_format)
                    rxx = fvv - fv
                    diasf = rxx.days
                    self.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    self.diasdif = diasf + 1  # DIAS DE DIFERENCIA ENTRE EST
                    self.diasperiodo = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                    self.montodiario_programado = self.monto_programado_est / self.diasdif  # MONTO DIARIO PROGRAMADO
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if self.montodiario_programado == 0:
                        self.montodiario_programado = 1
                    self.diasrealesrelacion = self.montoreal / self.montodiario_programado
                    if self.diasdif <= self.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                        self.dias_desfasamiento = 0
                    else:
                        self.dias_desfasamiento = self.diasdif - self.diasrealesrelacion

                    self.monto_atraso = self.dias_desfasamiento * self.montodiario_programado  # MONTO DE ATRASO
                    # PORCENTAJE ESTIMADO
                    self.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    self.porc_total_ret = self.retencion * self.dias_desfasamiento
                    self.total_ret_est = (self.monto_atraso * self.porc_total_ret) / 100
                    if self.retenido_anteriormente == 0:  # RETENCION
                        if self.montoreal > self.monto_programado_est:  # SI NO ES RET NI DEV
                            self.ret_neta_est = 0
                            self.devolucion_est = 0
                        else:
                            self.ret_neta_est = self.total_ret_est * -1
                            self.devolucion_est = 0
                    elif (self.retenido_anteriormente * -1) > 0 and self.total_ret_est == 0:  # DEVOLUCION
                        self.ret_neta_est = self.retenido_anteriormente * -1
                        self.devolucion_est = self.retenido_anteriormente * -1
                    elif self.retenido_anteriormente == 0 and self.total_ret_est == 0:
                        self.ret_neta_est = 0
                        self.devolucion_est = 0
                    elif (self.retenido_anteriormente * -1) <= self.total_ret_est:  # RETENCION
                        self.devolucion_est = 0
                        self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                    elif (self.retenido_anteriormente * -1) > self.total_ret_est:  # DEVOLUCION
                        self.ret_neta_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                        self.devolucion_est = (self.retenido_anteriormente * -1) - self.total_ret_est
                else:
                    print('no x2')
            else:
                print('se termino el cliclo xxxxxxxxxxxxxxxxxxx')
        print('---------------------------------xcxxxxxxxxxxxxxxxxxx-------------------------------')
        # --------... DATOS PARA SANCION ...-----------
        # BUSCAR FECHAS DEL PROGRAMA
        # b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', self.obra.id)])
        # VERIFICAR SI EXISTE CONVENIO

        fechaterminosancion = ""
        for i in b_programa.programa_contratos:
            fechaterminosancion = i.fecha_termino
            fecha_termino_programa = i.fecha_termino

        '''if _search_cove > 0:
            for i in b_convenio:
                if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                    fecha_prog = datetime.strptime(str(i.plazo_fecha_inicio), "%Y-%m-%d").date()
                    fecha_inicio_programa = fecha_prog
                    fecha_prog2 = datetime.strptime(str(i.plazo_fecha_termino), "%Y-%m-%d").date()
                    fecha_termino_programa = fecha_prog2
        else:
            # FECHA INICIO Y TERMINO DEL PROGRAMA
            fecha_inicio_programa = b_programa.fecha_inicio_programa
            fecha_termino_programa = b_programa.fecha_termino_programa'''

        estimacion_search = self.env['control.estimaciones'].search([('obra', '=', self.obra.id)])
        b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.obra.id)])
        f_estimacion_termino = self.fecha_termino_estimacion

        
        # SI LA ESTIMACION TERMINA EN EL MISM ODIA DEL PROGRAMA Y TIENE MONTOS QUE RETORNAR, LOS REGRESA
        '''if f_estimacion_termino == fecha_termino_programa:
            acum_ret_est = 0
            for i in estimacion_search:
                if not self.idobra or self.idobra is False:
                    acum_ret_est += i.ret_neta_est
                elif int(i.idobra) >= int(self.idobra):
                    print('pasar')
                else:
                    acum_ret_est += i.ret_neta_est

            self.ret_neta_est = (acum_ret_est * -1)
            self.devolucion_est = (acum_ret_est * -1)'''

        if self.si_aplica_estimacion:
            acum_ret_est = 0
            for i in estimacion_search:
                if not self.idobra:
                    if int(i.idobra) >= int(b_est_count + 1):
                        pass
                    else:
                        acum_ret_est += i.ret_neta_est
                else:
                    if int(i.idobra) >= int(b_est_count):
                        pass
                    else:
                        acum_ret_est += i.ret_neta_est

            self.ret_neta_est = (acum_ret_est * -1)
            self.devolucion_est = (acum_ret_est * -1)
        # SACAR VALOR DEDUCCIONES
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })
            if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                rec.update({
                    'valor': self.sub_total_esc_h * rec.porcentaje / 100
                })
        # SUMA DE DEDUCCIONES
        sumax = 0
        for i in self.deducciones:
            resultado = i.valor
            sumax = sumax + resultado
            self.estimado_deducciones = sumax

        # X-X-X-X-X-X-X-X-X--X  SANCION ------------------------------------------------------
        if f_estimacion_termino > fechaterminosancion:  # SANCION ///////////////////////////////////////////
            print(' APLICAR SANCION JUNTO ESTIMACION FINIQUITO')
            # acum_ret = 0
            termino_periodo_s = datetime.strptime(str(fecha_termino_programa), "%Y-%m-%d")
            termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
            
            resta = termino_estimacion_s - termino_periodo_s
            dias_sancion = resta.days
            if dias_sancion == 0:
                dias_sancion = 1
            # sancion = self.estimado * dias_sancion * self.porcentaje_sancion # 0.001

            '''search_saldo = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id),('tipo_estimacion', '=', "1"),
                                                                    ('sancion', '=', 0)],order='create_date asc', limit=1)
            # search_finiquitada = self.env['control.estimaciones'].search([('obra.id', '=', self.obra.id),('si_aplica_estimacion', '=', True)])[-1]

            saldo_contrato = 0
            saldo_contrato_finiquitado = 0
            if not search_saldo:
                saldo_contrato = 0
            else:
                saldo_contrato = search_saldo.saldo_contrato'''

            #self.ret_neta_est = 0
            #self.devolucion_est = 0
        else:
            self.sancion = 0
            self.dias_atraso_sancion = 0

        # --------... TERMINA DATOS PARA SANCION ...-----------

        if self.si_aplica_amortizar == True:  # VERIFICAR SI APLICA AMORTIZACION
            # CALCULAR ESTIMACION NETA SIN IVA
            if self.sub_total_esc > 0:
                self.estimacion_subtotal = self.sub_total_esc_h
            else:
                self.estimacion_subtotal = self.estimado - self.amort_anticipo

            # METODO PARA CALCULAR ESTIMACION IVA.
            self.estimacion_iva = (self.estimado - self.amort_anticipo) * self.b_iva

            # METODO PARA CALCULAR ESTIMACION + IVA
            self.estimacion_facturado = self.estimacion_subtotal + self.estimacion_iva

            # SANCION
            if f_estimacion_termino > fechaterminosancion: 
                sancion = (self.porcentaje_sancion * round(self.estimacion_subtotal, 2)) * dias_sancion
                self.sancion = round(sancion, 2)
                self.dias_atraso_sancion = dias_sancion
        
            # IMPORTE LIQUIDO
            for rec in self:
                if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                    self.sancion = 0
                    self.devolucion_est = 0
                    self.ret_neta_est = 0
                if self.sancion > 0:
                    rec.update({
                        # SE SANCION
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (
                            self.sancion) + self.ret_neta_est 
                    })
                elif self.retenido_anteriormente <= self.total_ret_est:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (
                                    self.ret_neta_est * -1)
                    })

                elif self.retenido_anteriormente > self.total_ret_est:
                    # SE DEVUELVE
                    rec.update({
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est
                    })

            # AMORTIZACION ANTICIPO
            acum_amort = 0
            print(' AMORTIZIPO AQui')
            for x in estimacion_search:
                if not self.idobra:
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) > int(x.idobra):
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) < int(x.idobra):
                    pass
            if self.idobra == '':
                self.amort_anticipo = self.obra.anticipo_a - acum_amort
            else:
                self.amort_anticipo = self.obra.anticipo_a - acum_amort
        else:
            print(' AMORT NORMAL')
            # self.amort_anticipo = self.amort_anticipo_partida * self.estimado
            acum_amort = 0
            for x in estimacion_search:
                if not self.idobra:
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) < int(x.idobra):
                    pass
                elif int(self.idobra) > int(x.idobra):
                    acum_amort += x.amort_anticipo
            if not self.idobra:
                amort_actual = (self.amort_anticipo_partida * self.estimado)
                acum_amortizado = acum_amort + amort_actual
                if acum_amortizado >= float(self.obra.anticipo_a):
                    # acum_total_anti = acum_amortizado # + (self.amort_anticipo_partida * self.estimado)
                    self.amort_anticipo = self.obra.anticipo_a - acum_amort  # 0
                elif float(self.obra.anticipo_a) == float(acum_amort):
                    self.amort_anticipo = 0
                else:
                    self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)
            else:
                # de lo contratio
                # self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)

                if acum_amort >= float(self.obra.anticipo_a):
                    self.amort_anticipo = 0
                elif float(self.obra.anticipo_a) == float(acum_amort):
                    self.amort_anticipo = 0
                else:
                    if float(self.amort_anticipo + acum_amort) > float(self.obra.anticipo_a):
                        # acum_total_anti = acum_amort
                        self.amort_anticipo = self.obra.anticipo_a - acum_amort
                    else:
                        self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)

            # CALCULAR ESTIMACION NETA SIN IVA
            if self.sub_total_esc > 0:
                self.estimacion_subtotal = self.sub_total_esc_h
            else:
                self.estimacion_subtotal = self.estimado - self.amort_anticipo
            self.estimacion_iva = (
                                            self.estimado - self.amort_anticipo) * self.b_iva  # METODO PARA CALCULAR ESTIMACION IVA.
            self.estimacion_facturado = self.estimacion_subtotal + self.estimacion_iva  # METODO PARA CALCULAR ESTIMACION + IVA
            
            if f_estimacion_termino > fechaterminosancion: 
                sancion = (dias_sancion * self.porcentaje_sancion) * self.estimacion_subtotal 
                self.sancion = sancion
                self.dias_atraso_sancion = dias_sancion
            
            # IMPORTE LIQUIDO
            for rec in self:
                if self.sancion > 0:
                    print('IMPORTE LIQUIDO CON SANSION')
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est - self.sancion
                    })
                elif self.retenido_anteriormente <= self.total_ret_est:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (
                                    self.ret_neta_est * -1)
                    })

                elif self.retenido_anteriormente > self.total_ret_est:
                    # SE DEVUELVE
                    rec.update({
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est
                    })


    # METODO PARA JALAR IMPORTE DE LOS CONCEPTOS DE PARTIDA
    @api.multi
    @api.onchange('amort_anticipo')
    def amort_anticipo_manual(self):  
        # CALCULAR ESTIMACION NETA SIN IVA
        if self.sub_total_esc > 0:
            self.estimacion_subtotal = self.sub_total_esc_h
        else:
            self.estimacion_subtotal = self.estimado - self.amort_anticipo

        # METODO PARA CALCULAR ESTIMACION IVA.
        self.estimacion_iva = (self.estimado - self.amort_anticipo) * self.b_iva

        # METODO PARA CALCULAR ESTIMACION + IVA
        self.estimacion_facturado = self.estimacion_subtotal + self.estimacion_iva
        # IMPORTE LIQUIDO
        for rec in self:
            if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                self.sancion = 0
                self.devolucion_est = 0
                self.ret_neta_est = 0

            if self.sancion > 0:
                if self.retenido_anteriormente <= self.total_ret_est:
                    rec.update({
                    # SE RETIENE
                    'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - ( self.sancion) - (self.ret_neta_est * -1)
                })

                elif self.retenido_anteriormente > self.total_ret_est:
                    # SE DEVUELVE
                    rec.update({
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - ( self.sancion) + self.devolucion_est
                    })

                
            # ------------------------------------------------------------------------
            elif self.retenido_anteriormente <= self.total_ret_est: # NORMAL
                rec.update({
                    # SE RETIENE
                    'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (self.ret_neta_est * -1)
                })

            elif self.retenido_anteriormente > self.total_ret_est:
                # SE DEVUELVE
                rec.update({
                    'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est
                })

    # METODO PARA JALAR IMPORTE DE LOS CONCEPTOS DE PARTIDA
    @api.multi
    @api.onchange('amort_anticipo_partida', 'si_aplica_amortizar')
    def amortizacion_anticipo_metodo(self):  # suma_conceptos
        estimacion_search = self.env['control.estimaciones'].search([('obra', '=', self.obra.id)])
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

        if self.si_aplica_amortizar == True:
            # CALCULAR ESTIMACION NETA SIN IVA
            if self.sub_total_esc > 0:
                self.estimacion_subtotal = self.sub_total_esc_h
            else:
                self.estimacion_subtotal = self.estimado - self.amort_anticipo

            # METODO PARA CALCULAR ESTIMACION IVA.
            self.estimacion_iva = (self.estimado - self.amort_anticipo) * self.b_iva

            # METODO PARA CALCULAR ESTIMACION + IVA
            self.estimacion_facturado = self.estimacion_subtotal + self.estimacion_iva
            # IMPORTE LIQUIDO
            for rec in self:
                print(self.sancion, ' ESTA ES LA SANCION A AP,ICAR ')
                if self.sancion > 0:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (
                            self.sancion)
                    })
                elif self.retenido_anteriormente <= self.total_ret_est:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (self.ret_neta_est * -1)
                    })

                elif self.retenido_anteriormente > self.total_ret_est:
                    # SE DEVUELVE
                    rec.update({
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est
                    })

            # AMORTIZACION ANTICIPO

            acum_amort = 0
            print(' AMORTIZIPO AQui')
            for x in estimacion_search:
                if not self.idobra:
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) > int(x.idobra):
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) < int(x.idobra):
                    pass
            if self.idobra == '':
                self.amort_anticipo = self.obra.anticipo_a - acum_amort
            else:
                self.amort_anticipo = self.obra.anticipo_a - acum_amort
        else:
            print( ' AMORT NORMAL')
            self.amort_anticipo = self.amort_anticipo_partida * self.estimado
            acum_amort = 0
            for x in estimacion_search:
                if not self.idobra:
                    acum_amort += x.amort_anticipo
                elif int(self.idobra) < int(x.idobra):
                    pass
                elif int(self.idobra) > int(x.idobra):
                    acum_amort += x.amort_anticipo
            if not self.idobra:
                if self.si_aplica_amortizar == True:  # preguntar si es amortizar todox completo anticipo
                    self.amort_anticipo = self.obra.anticipo_a - acum_amort
                elif float(self.obra.anticipo_a) == float(acum_amort):
                        self.amort_anticipo = 0
                else:
                    self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)
                    acum_amort = acum_amort + self.amort_anticipo
                    if acum_amort >= float(self.obra.anticipo_a):
                        self.amort_anticipo = 0
                    else:
                        if float(self.amort_anticipo + acum_amort) > float(self.obra.anticipo_a):
                            acum_total_anti = acum_amort + self.amort_anticipo
                            self.amort_anticipo = self.obra.anticipo_a - acum_total_anti
                        else:
                            self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)
            else:
                if self.si_aplica_amortizar == True:  # preguntar si es amortizar todox completo anticipo
                    self.amort_anticipo = self.obra.anticipo_a - acum_amort
                else:
                    # de lo contratio
                    self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)

                    if acum_amort >= float(self.obra.anticipo_a):
                        self.amort_anticipo = 0
                    elif float(self.obra.anticipo_a) == float(acum_amort):
                        self.amort_anticipo = 0
                    else:
                        if float(self.amort_anticipo + acum_amort) > float(self.obra.anticipo_a):
                            acum_total_anti = acum_amort
                            self.amort_anticipo = self.obra.anticipo_a - acum_total_anti
                        else:
                            self.amort_anticipo = (self.amort_anticipo_partida * self.estimado)
            # CALCULAR ESTIMACION NETA SIN IVA
            if self.sub_total_esc > 0:
                self.estimacion_subtotal = self.sub_total_esc_h
            else:
                self.estimacion_subtotal = self.estimado - self.amort_anticipo

            # METODO PARA CALCULAR ESTIMACION IVA.
            self.estimacion_iva = (self.estimado - self.amort_anticipo) * self.b_iva

            # METODO PARA CALCULAR ESTIMACION + IVA
            self.estimacion_facturado = self.estimacion_subtotal + self.estimacion_iva
            # IMPORTE LIQUIDO
            for rec in self:
                print(self.sancion, ' ESTA ES LA SANCION A AP,ICAR ')
                if self.sancion > 0:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (
                            self.sancion)
                    })
                elif self.retenido_anteriormente <= self.total_ret_est:
                    rec.update({
                        # SE RETIENE
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) - (self.ret_neta_est * -1)
                    })

                elif self.retenido_anteriormente > self.total_ret_est:
                    # SE DEVUELVE
                    rec.update({
                        'a_pagar': (self.estimacion_facturado - self.estimado_deducciones) + self.devolucion_est
                    })