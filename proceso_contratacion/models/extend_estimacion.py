# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date
from datetime import datetime
import calendar
import warnings


class ConceptosDetalleExtend(models.Model):
    _inherit = 'control.detalle_conceptos'

    '''@api.multi
    @api.onchange('estimacion')
    def EstimadoEstimacion(self):
        b_estx = self.env['control.estimaciones'].search([('obra.id', '=', self.id_partida.id),('idobra', '=', self.num_est)])
        b_conceptos = self.env['control.detalle_conceptos'].search([('id_partida.id', '=', self.id_partida.id),
                                                                    ('num_est', '=', self.num_est)])
        importe_ejecutado = self.estimacion * self.precio_unitario

        b_est = self.env['control.estimaciones'].browse(b_estx.id)
        # SACAMOS EL TOTAL ESTIMADO DE LOS CONCEPTOS
        suma = 0
        for t in b_conceptos:
            if t.clave_linea == self.clave_linea:
                suma += importe_ejecutado
            else:
                suma += t.importe_ejecutado

        datos_estimacion = {
            'estimado': suma
        }
        b_est.write(datos_estimacion) # MANDAR EL ESTIMADO A LA ESTIMACION

        for x in b_estx:
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', self.id_partida.id)])
            b_est_metodo = self.env['control.estimaciones'].search([('obra.id', '=', self.id_partida.id)])
            # ACUMULAMOS RETENIDOS ANTERIORES
            acum_Ret = 0
            for y in b_est_metodo:
                if not y.idobra:
                    if not y.idobra:
                        break
                    else:
                        acum_Ret += y.ret_neta_est
                else:
                    if int(x.idobra) <= int(y.idobra):
                        pass
                    else:
                        acum_Ret += y.ret_neta_est

            # ESCALATORIA
            if x.tipo_estimacion == '2':
                x.estimado = x.sub_total_esc_h
                suma = x.sub_total_esc_h

            x.estimado = suma # ESTIMADO

            # MONTO ACTUAL A EJECUTAR ESTIMADO
            acum_real = 0
            for i in b_est_metodo:
                if not x.idobra:
                    acum_real = acum_real + i.estimado
                    x.montoreal = acum_real + x.estimado
                elif int(i.idobra) <= int(x.idobra):
                    acum_real = acum_real + i.estimado
                    x.montoreal = acum_real

            # RETENIDO ANTERIORMENTE
            x.retenido_anteriormente = acum_Ret
            if int(b_est_count) == 0 or int(x.idobra) == 1:
                x.retenido_anteriormente = 0

            x.nuevo_metodo = True  # INDICA SI ES NUEVA ESTIMACION, NO IMPORTADA DE SIDEOP PARA CONDICION DE QWEB
            # FECHA INICIO Y TERMINO ESTIMACION
            f_estimacion_inicio = x.fecha_inicio_estimacion
            f_estimacion_termino = x.fecha_termino_estimacion
            # DIA DE TERMINO DE LA ESTIMACION
            f_est_termino_dia = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
            # BUSCAR FECHAS DEL PROGRAMA
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', x.obra.id)])
            # VERIFICAR SI EXISTE CONVENIO
            _search_cove = self.env['proceso.convenios_modificado'].search_count(
                [("nombre_contrato", "=", x.obra.nombre_contrato), ("tipo_convenio", "=", 'PL' or 'BOTH')])
            b_convenio = self.env['proceso.convenios_modificado'].search(
                [('nombre_contrato', '=', x.obra.nombre_contrato)])
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
            fe1 = fecha_inicio_programa
            fe2 = fecha_termino_programa
            if fe1 and fe2:
                f1h = datetime.strptime(str(fe1), "%Y-%m-%d")
                f2h = datetime.strptime(str(fe2), "%Y-%m-%d")
                rh = f2h - f1h
                x.dias_transcurridos = rh.days + 1

            monto_contrato = b_programa.total_programa
            # NUMERO DE DIAS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO DE ESTA
            diasest = calendar.monthrange(f_estimacion_termino.year, f_estimacion_termino.month)[1]
            acum = 0
            cont = 0
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
                print('CON LA ESTIMACION #', x.idobra, ' +++++')
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

                    b_programa_c = self.env['proceso.programa'].search_count([('obra.id', '=', x.obra.id)])
                    if b_programa_c == 1:
                        monto_final = (i.monto / (dias + 1)) * ff
                        m_estimado = acum + monto_final
                    elif x.idobra == 1 or b_est_count == 0:
                        monto_final = 0
                        m_estimado = (acum - i.monto) + monto_final
                    else:
                        # monto_final = (i.monto / (dias + 1)) * ff
                        monto_final = (i.monto / (dia_inicio_atermino + 1)) * (dias_trans_mesactual + 1)
                        m_estimado = (acum - i.monto) + monto_final

                    x.ultimomonto = monto_final
                    x.diasest = diasest
                    x.diastransest = ff2
                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    x.monto_programado_est = m_estimado
                    # x.reduccion = monto_final
                    # DIAS DE DIFERENCIA ENTRE EST
                    x.diasdif = dias + 1
                    # TOTAL DIAS PERIODO PROGRAMA
                    x.diasperiodo = total_dias_periodo
                    # MONTO DIARIO PROGRAMADO
                    x.montodiario_programado = x.monto_programado_est / x.diasdif
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    if x.montodiario_programado == 0:
                        x.montodiario_programado = 1
                    x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                    # DIAS DE DESFASAMIENTO
                    if x.dias_transcurridos <= x.diasrealesrelacion:
                        x.dias_desfasamiento = 0
                    else:
                        x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                    # MONTO DE ATRASO
                    x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado
                    # PORCENTAJE ESTIMADO
                    x.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    x.porc_total_ret = x.retencion * x.dias_desfasamiento
                    x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                    if x.retenido_anteriormente == 0:  # RETENCION
                        if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                            x.ret_neta_est = 0
                            x.devolucion_est = 0
                        else:
                            x.ret_neta_est = x.total_ret_est * -1
                            x.devolucion_est = 0
                    elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                        x.ret_neta_est = x.retenido_anteriormente * -1
                        x.devolucion_est = x.retenido_anteriormente * -1
                    elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                        x.ret_neta_est = 0
                        x.devolucion_est = 0
                    elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                        x.devolucion_est = 0
                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                    elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                        x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est

                    datos = {
                        'diasest': x.diasest,
                        'diastransest': x.diastransest,
                        'monto_programado_est': x.monto_programado_est,
                        'diasdif': x.diasdif,
                        'diasperiodo': x.diasperiodo,
                        'montodiario_programado': x.montodiario_programado,
                        'diasrealesrelacion': x.diasrealesrelacion,
                        'dias_transcurridos': x.dias_transcurridos,
                        'monto_atraso': x.monto_atraso,
                        'porcentaje_est': x.porcentaje_est,
                        'porc_total_ret': x.porc_total_ret,
                        'total_ret_est': x.total_ret_est,
                        'retenido_anteriormente': x.retenido_anteriormente,
                        'ret_neta_est': x.ret_neta_est,
                        'devolucion_est': x.devolucion_est,
                    }
                    b_est.write(datos)

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
                    x.diastransest = dias_trans
                    # MONTO PROGRAMADO PARA ESTA ESTIMACION
                    x.monto_programado_est = m_estimado
                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                    r = f2 - f1
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE HASTA EL
                    # TERMINO DE LA ESTIMACION
                    dias = r.days + 1
                    x.diasdif = dias

                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                    r2 = f4 - f3
                    # DIAS DEL PERIODO
                    total_dias_periodo = r2.days
                    x.diasperiodo = total_dias_periodo

                    # MONTO DIARIO PROGRAMADO
                    x.montodiario_programado = x.monto_programado_est / x.diasdif
                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                    x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                    # DIAS DE DESFASAMIENTO
                    if x.dias_transcurridos <= x.diasrealesrelacion:
                        x.dias_desfasamiento = 0
                    else:
                        x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                    # MONTO DE ATRASO
                    x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado
                    # PORCENTAJE ESTIMADO
                    x.porcentaje_est = (m_estimado / monto_contrato) * 100
                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                    x.porc_total_ret = x.retencion * x.dias_desfasamiento
                    x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                    if x.retenido_anteriormente == 0:  # RETENCION
                        if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                            x.ret_neta_est = 0
                            x.devolucion_est = 0
                        else:
                            x.ret_neta_est = x.total_ret_est * -1
                            x.devolucion_est = 0
                    elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                        x.ret_neta_est = x.retenido_anteriormente * -1
                        x.devolucion_est = x.retenido_anteriormente * -1
                    elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                        x.ret_neta_est = 0
                        x.devolucion_est = 0
                    elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                        x.devolucion_est = 0
                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                    elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                        x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est

                    datos = {
                        'diasest': x.diasest,
                        'diastransest': x.diastransest,
                        'monto_programado_est': x.monto_programado_est,
                        'diasdif': x.diasdif,
                        'diasperiodo': x.diasperiodo,
                        'montodiario_programado': x.montodiario_programado,
                        'diasrealesrelacion': x.diasrealesrelacion,
                        'dias_transcurridos': x.dias_transcurridos,
                        'monto_atraso': x.monto_atraso,
                        'porcentaje_est': x.porcentaje_est,
                        'porc_total_ret': x.porc_total_ret,
                        'total_ret_est': x.total_ret_est,
                        'retenido_anteriormente': x.retenido_anteriormente,
                        'ret_neta_est': x.ret_neta_est,
                        'devolucion_est': x.devolucion_est,
                    }
                    b_est.write(datos)

                # SI EL DIA DE LA FECHA TERMINO DE LA ESTIMACION ES IGUAL AL DIA ULTIMO DEL MES
                elif f_est_termino_dia.day == diasest:
                    # FECHA TERMINO PROGRAMA MES Y AÑO ES MAYOR A FECHAR TERMINO ESTIMACION MES Y AÑO TERMINAR CICLO
                    if fechatermino <= x.fecha_termino_estimacion:
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
                        x.diasest = diasest
                        x.diastransest = diastransest
                        x.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                        x.diasdif = dias + 1  # DIAS DE DIFERENCIA ENTRE EST
                        x.diasperiodo = total_dias_periodo  # TOTAL DIAS PERIODO PROGRAMA
                        x.montodiario_programado = x.monto_programado_est / x.diasdif  # MONTO DIARIO PROGRAMADO
                        if x.montodiario_programado == 0:  # DIAS EJECUTADOS REALES
                            x.montodiario_programado = 1  # CON RELACION AL
                        x.diasrealesrelacion = x.montoreal / x.montodiario_programado  # MONTO DIARIO PROGRAMADO
                        if x.dias_transcurridos <= x.diasrealesrelacion:  # DIAS DE DESFASAMIENTO
                            x.dias_desfasamiento = 0
                        else:
                            x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                        x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado  # MONTO DE ATRASO
                        x.porcentaje_est = (m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                        x.porc_total_ret = x.retencion * x.dias_desfasamiento  # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                        if x.retenido_anteriormente == 0:  # RETENCION
                            if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                                x.ret_neta_est = 0
                                x.devolucion_est = 0
                            else:
                                x.ret_neta_est = x.total_ret_est * -1
                                x.devolucion_est = 0
                        elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                            x.ret_neta_est = x.retenido_anteriormente * -1
                            x.devolucion_est = x.retenido_anteriormente * -1
                        elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                            x.ret_neta_est = 0
                            x.devolucion_est = 0
                        elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                            x.devolucion_est = 0
                            x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                        elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                            x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                            x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                        datos = {
                            'diasest': x.diasest,
                            'diastransest': x.diastransest,
                            'monto_programado_est': x.monto_programado_est,
                            'diasdif': x.diasdif,
                            'diasperiodo': x.diasperiodo,
                            'montodiario_programado': x.montodiario_programado,
                            'diasrealesrelacion': x.diasrealesrelacion,
                            'dias_transcurridos': x.dias_transcurridos,
                            'monto_atraso': x.monto_atraso,
                            'porcentaje_est': x.porcentaje_est,
                            'porc_total_ret': x.porc_total_ret,
                            'total_ret_est': x.total_ret_est,
                            'retenido_anteriormente': x.retenido_anteriormente,
                            'ret_neta_est': x.ret_neta_est,
                            'devolucion_est': x.devolucion_est,
                        }
                        b_est.write(datos)
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
                        esti = self.env['control.estimaciones'].search([('obra.id', '=', x.obra.id), ('idobra', '=', str(self.num_est))])
                        if fecha_terminoest_y_m == fecha_terminop_y_m:
                            for x in esti:
                                if int(x.idobra) > int(x.idobra) or int(x.idobra) > (b_est_count + 1):
                                    # SI NO ES LA ULTIMA ESTIMACION ENTONCES
                                    pass
                                elif x.idobra == x.idobra or int(x.idobra) == (b_est_count + 1):
                                    print(
                                        '#2 COINCIDE CON EL ULTIMO MES DEL PROGRAMA CUANDO SON MESES DIFERENTES')
                                    diasestx = \
                                    calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                        1]
                                    fx = datetime.strptime(str(f_estimacion_inicio), date_format)
                                    fy = datetime.strptime(str(f_estimacion_termino), date_format)
                                    rx = fy - fx
                                    diastransestx = rx.days # DIAS TRANSCURRIDOS DE LA ESTIMACION
                                    ultimo_monto = i.monto # MONTO CORRESPONDIENTE A LA FECHA DE ESTIMACION CON LA DEL PROGRAMA
                                    x1 = acum - ultimo_monto
                                    x2 = i.monto / diasestx
                                    m_estimado = x1 + x2 * (diastransestx + 1)
                                    x.diasest = diasestx
                                    x.diastransest = diastransestx
                                    x.monto_programado_est = m_estimado  # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                    f1 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                                    r = f2 - f1
                                    dias = r.days + 1  # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA CORRESPONDIENTE
                                    x.diasdif = dias  # HASTA EL TERMINO DE LA ESTIMACION
                                    f3 = datetime.strptime(str(fecha_inicio_programa), date_format)
                                    f4 = datetime.strptime(str(fecha_termino_programa), date_format)
                                    r2 = f4 - f3
                                    total_dias_periodo = r2.days
                                    x.diasperiodo = total_dias_periodo  # DIAS DEL PERIODO
                                    x.montodiario_programado = x.monto_programado_est / x.diasdif  # MONTO DIARIO PROGRAMADO
                                    # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                    x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                                    if x.dias_transcurridos <= x.diasrealesrelacion:
                                        x.dias_desfasamiento = 0
                                    else:
                                        x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion  # DIAS DE DESFASAMIENTO
                                    x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado  # MONTO DE ATRASO
                                    x.porcentaje_est = (
                                                                      m_estimado / monto_contrato) * 100  # PORCENTAJE ESTIMADO
                                    # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                    x.porc_total_ret = x.retencion * x.dias_desfasamiento
                                    x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                                    if x.retenido_anteriormente == 0:  # RETENCION
                                        if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                                            x.ret_neta_est = 0
                                            x.devolucion_est = 0
                                        else:
                                            x.ret_neta_est = x.total_ret_est * -1
                                            x.devolucion_est = 0
                                    elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                                        x.ret_neta_est = x.retenido_anteriormente * -1
                                        x.devolucion_est = x.retenido_anteriormente * -1
                                    elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                                        x.ret_neta_est = 0
                                        x.devolucion_est = 0
                                    elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                                        x.devolucion_est = 0
                                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                    elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                                        x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                        x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est

                                    datos = {
                                        'diasest': x.diasest,
                                        'diastransest': x.diastransest,
                                        'monto_programado_est': x.monto_programado_est,
                                        'diasdif': x.diasdif,
                                        'diasperiodo': x.diasperiodo,
                                        'montodiario_programado': x.montodiario_programado,
                                        'diasrealesrelacion': x.diasrealesrelacion,
                                        'dias_transcurridos': x.dias_transcurridos,
                                        'monto_atraso': x.monto_atraso,
                                        'porcentaje_est': x.porcentaje_est,
                                        'porc_total_ret': x.porc_total_ret,
                                        'total_ret_est': x.total_ret_est,
                                        'retenido_anteriormente': x.retenido_anteriormente,
                                        'ret_neta_est': x.ret_neta_est,
                                        'devolucion_est': x.devolucion_est,
                                    }
                                    b_est.write(datos)

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
                            diasest = calendar.monthrange(f_estimacion_inicio.year, f_estimacion_inicio.month)[
                                1]
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
                                        print('fin')
                                    elif dat3 > dat:
                                        print('terminar')
                                    elif dat3 <= dat:
                                        acum_ftemtp += c.monto
                                        print('acumular')
                                        cx += 1
                                    '''elif dat4 > f_sansion:
                                        print('SANSION TERMINAR')'''

                                ultimo_monto = b_programa.programa_contratos[int(cx)].monto

                                f_pt = datetime.strptime(
                                    str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                    date_format)
                                f_et = datetime.strptime(str(f_estimacion_termino), date_format)
                                ry = f_et - f_pt
                                d_entre_fecha = ry.days
                                ff_inicio = datetime.strptime(
                                    str(b_programa.programa_contratos[int(cx)].fecha_inicio),
                                    date_format)
                                ff_termino = datetime.strptime(
                                    str(b_programa.programa_contratos[int(cx)].fecha_termino), date_format)
                                rf = ff_termino - ff_inicio
                                diastransestx = rf.days + 1
                                formula = (ultimo_monto / diastransestx) * (d_entre_fecha + 1)
                                acumulado = acum_ftemtp
                                m_estimado = acumulado + formula  # * (diastransest + 1)
                                x.ultimomonto = ultimo_monto
                                x.diasest = diasest
                                x.diastransest = diastransestx
                                x.monto_programado_est = m_estimado # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                x.diasdif = dias + 1 # DIAS DE DIFERENCIA ENTRE EST
                                x.diasperiodo = total_dias_periodo # TOTAL DIAS PERIODO PROGRAMA
                                x.montodiario_programado = x.monto_programado_est / x.diasdif # MONTO DIARIO PROGRAMADO
                                if x.montodiario_programado == 0:
                                    x.montodiario_programado = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                                # DIAS DE DESFASAMIENTO
                                if x.dias_transcurridos <= x.diasrealesrelacion:
                                    x.dias_desfasamiento = 0
                                else:
                                    x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                                x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado # MONTO DE ATRASO
                                x.porcentaje_est = (m_estimado / monto_contrato) * 100 # PORCENTAJE ESTIMADO
                                # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                x.porc_total_ret = x.retencion * x.dias_desfasamiento

                                x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                                if x.retenido_anteriormente == 0:  # RETENCION
                                    if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                                        x.ret_neta_est = 0
                                        x.devolucion_est = 0
                                    else:
                                        x.ret_neta_est = x.total_ret_est * -1
                                        x.devolucion_est = 0
                                elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                                    x.ret_neta_est = x.retenido_anteriormente * -1
                                    x.devolucion_est = x.retenido_anteriormente * -1
                                elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                                    x.ret_neta_est = 0
                                    x.devolucion_est = 0
                                elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                                    x.devolucion_est = 0
                                    x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                                    x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                    x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                datos = {
                                    'diasest': x.diasest,
                                    'diastransest': x.diastransest,
                                    'monto_programado_est': x.monto_programado_est,
                                    'diasdif': x.diasdif,
                                    'diasperiodo': x.diasperiodo,
                                    'montodiario_programado': x.montodiario_programado,
                                    'diasrealesrelacion': x.diasrealesrelacion,
                                    'dias_transcurridos': x.dias_transcurridos,
                                    'monto_atraso': x.monto_atraso,
                                    'porcentaje_est': x.porcentaje_est,
                                    'porc_total_ret': x.porc_total_ret,
                                    'total_ret_est': x.total_ret_est,
                                    'retenido_anteriormente': x.retenido_anteriormente,
                                    'ret_neta_est': x.ret_neta_est,
                                    'devolucion_est': x.devolucion_est,
                                }
                                b_est.write(datos)
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
                                    [('obra.id', '=', x.obra.id)])
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
                                x.ultimomonto = ultimo_monto
                                x.diasest = diasest
                                x.diastransest = diastransest
                                x.monto_programado_est = m_estimado # MONTO PROGRAMADO PARA ESTA ESTIMACION
                                x.diasdif = dias + 1 # DIAS DE DIFERENCIA ENTRE EST
                                x.diasperiodo = total_dias_periodo # TOTAL DIAS PERIODO PROGRAMA
                                x.montodiario_programado = x.monto_programado_est / x.diasdif # MONTO DIARIO PROGRAMADO
                                if x.montodiario_programado == 0:
                                    x.montodiario_programado = 1
                                # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                                x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                                if x.dias_transcurridos <= x.diasrealesrelacion: # DIAS DE DESFASAMIENTO
                                    x.dias_desfasamiento = 0
                                else:
                                    # x.dias_desfasamiento = x.dias_transcurridos - x.diasrealesrelacion
                                    x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                                x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado # MONTO DE ATRASO
                                x.porcentaje_est = (m_estimado / monto_contrato) * 100 # PORCENTAJE ESTIMADO
                                x.porc_total_ret = x.retencion * x.dias_desfasamiento # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                                x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100
                                if x.retenido_anteriormente == 0:  # RETENCION
                                    if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                                        x.ret_neta_est = 0
                                        x.devolucion_est = 0
                                    else:
                                        x.ret_neta_est = x.total_ret_est * -1
                                        x.devolucion_est = 0
                                elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                                    x.ret_neta_est = x.retenido_anteriormente * -1
                                    x.devolucion_est = x.retenido_anteriormente * -1
                                elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                                    x.ret_neta_est = 0
                                    x.devolucion_est = 0
                                elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                                    x.devolucion_est = 0
                                    x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                                    x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                    x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                                datos = {
                                    'diasest': x.diasest,
                                    'diastransest': x.diastransest,
                                    'monto_programado_est': x.monto_programado_est,
                                    'diasdif': x.diasdif,
                                    'diasperiodo': x.diasperiodo,
                                    'montodiario_programado': x.montodiario_programado,
                                    'diasrealesrelacion': x.diasrealesrelacion,
                                    'dias_transcurridos': x.dias_transcurridos,
                                    'monto_atraso': x.monto_atraso,
                                    'porcentaje_est': x.porcentaje_est,
                                    'porc_total_ret': x.porc_total_ret,
                                    'total_ret_est': x.total_ret_est,
                                    'retenido_anteriormente': x.retenido_anteriormente,
                                    'ret_neta_est': x.ret_neta_est,
                                    'devolucion_est': x.devolucion_est,
                                }
                                b_est.write(datos)

                                    # elif f_termino_proglista <= fecha_terminoest_y_m:
                    elif f_termino_prog_todo <= fecha_terminoest_todo:
                        acum = acum + i.monto
                        print('CUANDO LA ESTIMACION ES MENOS DE 30 DIAS EN EL MES')
                        f1 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                        f2 = datetime.strptime(str(f_estimacion_termino), date_format)
                        r = f2 - f1
                        dias = r.days + 1 # DIAS TRANSCURRIDOS DESDE EL INICIO DE LA ESTIMACION HASTA EL TERMINO
                        dia_0 = datetime.strptime(str(f_estimacion_inicio.replace(day=1)), date_format)
                        dia_02 = datetime.strptime(str(f_estimacion_inicio), date_format)
                        dia_r = dia_02 - dia_0
                        dia_rr = dia_r.days # dia 0 del mes al dia de inicio de esti
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
                        if fechatermino < f_estimacion_termino:
                            formula = 1  # evitar errores
                        else:
                            if diastransest == diasest:
                                print(' termina en el dia ultimo del mes', diastransest, diasest)
                                # MONTO / DIAS DEL MES * NUMERO DE DIAS TRANSCURRIDOS DEL INICIO DEL MES DE LA EST AL TERMINO
                                formula = (i.monto / diasest) * diastransest
                            elif dia_progy < diasest:
                                print(' TERMINO PROG ES ANTES DEL MES')
                                formula = (i.monto / dia_progy) * diasx  # SIDUR-PF-18-220.1497
                            else:
                                # normal
                                print(' termina antes', diastransest, diasest)
                                # formula = (i.monto / (diasest - dia_rr)) * diasx
                                # formula = (i.monto / diasest) * diasx
                                formula = (i.monto / diasest) * dias  # SIDUR-ED-20-002.1873
                        x.ultimomonto = i.monto
                        if str(x.idobra) == '1' or int(b_est_count) == 0:
                            m_estimado = formula
                        else:
                            m_estimado = (acum - i.monto) + formula  # (i.monto - formula)
                        x.diasest = diasest
                        x.diastransest = diastransest + 1
                        fv = datetime.strptime(str(fecha_inicio_programa), date_format)
                        fvv = datetime.strptime(str(f_estimacion_termino), date_format)
                        rxx = fvv - fv
                        diasf = rxx.days
                        x.monto_programado_est = m_estimado # MONTO PROGRAMADO PARA ESTA ESTIMACION
                        x.diasdif = diasf + 1 # DIAS DE DIFERENCIA ENTRE EST
                        x.diasperiodo = total_dias_periodo # TOTAL DIAS PERIODO PROGRAMA
                        x.montodiario_programado = x.monto_programado_est / x.diasdif # MONTO DIARIO PROGRAMADO
                        # DIAS EJECUTADOS REALES CON RELACION AL MONTO DIARIO PROGRAMADO
                        if x.montodiario_programado == 0:
                            x.montodiario_programado = 1
                        x.diasrealesrelacion = x.montoreal / x.montodiario_programado
                        # DIAS DE DESFASAMIENTO
                        if x.dias_transcurridos <= x.diasrealesrelacion:
                            x.dias_desfasamiento = 0
                        else:
                            x.dias_desfasamiento = x.diasdif - x.diasrealesrelacion
                        # MONTO DE ATRASO
                        x.monto_atraso = x.dias_desfasamiento * x.montodiario_programado
                        # PORCENTAJE ESTIMADO
                        x.porcentaje_est = (m_estimado / monto_contrato) * 100
                        # TOTAL DE LA RETENCION HASTA ESTA ESTIMACION
                        x.porc_total_ret = x.retencion * x.dias_desfasamiento
                        x.total_ret_est = (x.monto_atraso * x.porc_total_ret) / 100

                        if x.retenido_anteriormente == 0:  # RETENCION
                            if x.montoreal > x.monto_programado_est: # SI NO ES RET NI DEV
                                x.ret_neta_est = 0
                                x.devolucion_est = 0
                            else:
                                x.ret_neta_est = x.total_ret_est * -1
                                x.devolucion_est = 0
                        elif (x.retenido_anteriormente * -1) > 0 and x.total_ret_est == 0:  # DEVOLUCION
                            x.ret_neta_est = x.retenido_anteriormente * -1
                            x.devolucion_est = x.retenido_anteriormente * -1
                        elif x.retenido_anteriormente == 0 and x.total_ret_est == 0:
                            x.ret_neta_est = 0
                            x.devolucion_est = 0
                        elif (x.retenido_anteriormente * -1) <= x.total_ret_est:  # RETENCION
                            x.devolucion_est = 0
                            x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                        elif (x.retenido_anteriormente * -1) > x.total_ret_est:  # DEVOLUCION
                            x.ret_neta_est = (x.retenido_anteriormente * -1) - x.total_ret_est
                            x.devolucion_est = (x.retenido_anteriormente * -1) - x.total_ret_est

                        
                        datos = {
                            'diasest': x.diasest,
                            'diastransest': x.diastransest,
                            'monto_programado_est': x.monto_programado_est,
                            'diasdif': x.diasdif,
                            'diasperiodo': x.diasperiodo,
                            'montodiario_programado': x.montodiario_programado,
                            'diasrealesrelacion': x.diasrealesrelacion,
                            'dias_transcurridos': x.dias_transcurridos,
                            'monto_atraso': x.monto_atraso,
                            'porcentaje_est': x.porcentaje_est,
                            'porc_total_ret': x.porc_total_ret,
                            'total_ret_est': x.total_ret_est,
                            'retenido_anteriormente': x.retenido_anteriormente,
                            'ret_neta_est': x.ret_neta_est,
                            'devolucion_est': x.devolucion_est,
                        }
                        b_est.write(datos)
                    else:
                        print('no x2')
                else:
                    print('se termino el cliclo xxxxxxxxxxxxxxxxxxx')
        print('---------------------------------xcxxxxxxxxxxxxxxxxxx-------------------------------')
        estimacion_search = self.env['control.estimaciones'].search([('obra.id', '=', self.id_partida.id), ('idobra', '=', str(self.num_est))])
        for x in estimacion_search:
            b_est = self.env['control.estimaciones'].browse(x.id)

            # --------... DATOS PARA SANCION ...-----------
            sancion = 0
            # BUSCAR FECHAS DEL PROGRAMA
            b_programa = self.env['programa.programa_obra'].search([('obra.id', '=', x.obra.id)])
            # VERIFICAR SI EXISTE CONVENIO
            _search_cove = self.env['proceso.convenios_modificado'].search_count(
                [("nombre_contrato", "=", x.obra.nombre_contrato), ("tipo_convenio", "=", 'PL' or 'BOTH')])
            b_convenio = self.env['proceso.convenios_modificado'].search(
                [('nombre_contrato', '=', x.obra.nombre_contrato)])
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

            estimacion_search = self.env['control.estimaciones'].search([('obra', '=', x.obra.id)])
            b_est_count = self.env['control.estimaciones'].search_count([('obra.id', '=', x.obra.id)])
            f_estimacion_termino = x.fecha_termino_estimacion
            if fecha_termino_programa < f_estimacion_termino:
                print(' APLICAR SANCION FINALx')
                acum_ret = 0
                termino_periodo_s = datetime.strptime(str(fecha_termino_programa), "%Y-%m-%d")
                termino_estimacion_s = datetime.strptime(str(f_estimacion_termino), "%Y-%m-%d")
                for u in estimacion_search:
                    if int(u.idobra) <= int(x.idobra) or int(u.idobra) <= int(b_est_count + 1):
                        if u.ret_neta_est < 0:
                            acum_ret += u.ret_neta_est
                        else:
                            pass
                        if u.sancion > 0:
                            acum_ret = 0
                    else:
                        pass
                resta = termino_estimacion_s - termino_periodo_s
                dias_sancion = resta.days
                if dias_sancion == 0:
                    dias_sancion = 1
                sancion = x.estimado * dias_sancion * 0.01
                sancion = sancion
                dias_atraso_sancion = dias_sancion
                datos_estimacion = {
                    'sancion': sancion, 'dias_atraso_sancion': dias_atraso_sancion,
                }
                b_est.write(datos_estimacion)
            # --------... TERMINA DATOS PARA SANCION ...-----------
            if x.si_aplica_estimacion == True: # VERFICAR SI APLICA FINIQUITO
                acum = 0
                ret = x.ret_neta_est
                for i in estimacion_search:
                    acum += i.ret_neta_est
                x.ret_neta_est = (acum * -1) - (ret * -1)
                x.devolucion_est = (acum * -1) - (ret * -1)
            # SACAR VALOR DEDUCCIONES
            for rec in x.deducciones:
                rec.write({
                    'valor': suma * rec.porcentaje / 100
                })
            # SUMA DE DEDUCCIONES
            sumax = 0
            for i in x.deducciones:
                resultado = i.valor
                sumax = sumax + resultado
            estimado_deducciones = sumax

            if x.si_aplica_amortizar == True: # VERIFICAR SI APLICA AMORTIZACION
                # CALCULAR ESTIMACION NETA SIN IVA
                if x.sub_total_esc > 0:
                    x.estimacion_subtotal = x.sub_total_esc_h
                else:
                    x.estimacion_subtotal = x.estimado - x.amort_anticipo

                # METODO PARA CALCULAR ESTIMACION IVA.
                x.estimacion_iva = (x.estimado - x.amort_anticipo) * x.b_iva

                # METODO PARA CALCULAR ESTIMACION + IVA
                x.estimacion_facturado = x.estimacion_subtotal + x.estimacion_iva

                datos_estimacion = {
                    'estimacion_iva': x.estimacion_iva, 'estimacion_facturado': x.estimacion_facturado,
                    'estimacion_subtotal': x.estimacion_subtotal, 'estimado_deducciones': estimado_deducciones
                }
                b_est.write(datos_estimacion)

                # IMPORTE LIQUIDO
                for rec in x:
                    if x.sancion > 0:
                        datos_san = {
                            # SE RETIENE
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) - (
                                x.sancion)
                        }
                        b_est.write(datos_san)
                    elif x.retenido_anteriormente <= x.total_ret_est:
                        datos_ret = {
                            # SANCION
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) -
                                       (sancion) + x.devolucion_est - (x.ret_neta_est * -1)
                        }
                        b_est.write(datos_ret)

                    elif x.retenido_anteriormente > x.total_ret_est:
                        # SE DEVUELVE
                        datos_pagar_dev = {
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) + x.devolucion_est
                        }

                        b_est.write(datos_pagar_dev)

                # AMORTIZACION ANTICIPO
                acum_amort = 0
                print(' AMORTIZIPO AQui')
                for x in estimacion_search:
                    if not x.idobra:
                        acum_amort += x.amort_anticipo
                    elif int(x.idobra) > int(x.idobra):
                        acum_amort += x.amort_anticipo
                    elif int(x.idobra) < int(x.idobra):
                        pass
                if x.idobra == '':
                    x.amort_anticipo = x.obra.anticipo_a - acum_amort
                else:
                    x.amort_anticipo = x.obra.anticipo_a - acum_amort

                datos_estimacion = {
                    'amort_anticipo': x.amort_anticipo
                }
                b_est.write(datos_estimacion)

            else:
                print(' AMORT NORMAL')
                x.amort_anticipo = x.amort_anticipo_partida * x.estimado
                acum_amort = 0
                for x in estimacion_search:
                    if not x.idobra:
                        acum_amort += x.amort_anticipo
                    elif int(x.idobra) < int(x.idobra):
                        pass
                    elif int(x.idobra) > int(x.idobra):
                        acum_amort += x.amort_anticipo
                if not x.idobra:
                    if x.si_aplica_amortizar == True:  # preguntar si es amortizar todox completo anticipo
                        x.amort_anticipo = x.obra.anticipo_a - acum_amort
                    else:
                        x.amort_anticipo = (x.amort_anticipo_partida * x.estimado)
                        acum_amort = acum_amort + x.amort_anticipo
                        if acum_amort >= float(x.obra.anticipo_a):
                            x.amort_anticipo = 0
                        else:
                            if float(x.amort_anticipo + acum_amort) > float(x.obra.anticipo_a):
                                acum_total_anti = acum_amort + x.amort_anticipo
                                x.amort_anticipo = x.obra.anticipo_a - acum_total_anti
                            else:
                                x.amort_anticipo = (x.amort_anticipo_partida * x.estimado)
                else:
                    if x.si_aplica_amortizar == True:  # preguntar si es amortizar todox completo anticipo
                        x.amort_anticipo = x.obra.anticipo_a - acum_amort
                    else:
                        # de lo contratio
                        x.amort_anticipo = (x.amort_anticipo_partida * x.estimado)

                        if acum_amort >= float(x.obra.anticipo_a):
                            x.amort_anticipo = 0
                        else:
                            if float(x.amort_anticipo + acum_amort) > float(x.obra.anticipo_a):
                                acum_total_anti = acum_amort
                                x.amort_anticipo = x.obra.anticipo_a - acum_total_anti
                            else:
                                x.amort_anticipo = (x.amort_anticipo_partida * x.estimado)

                # CALCULAR ESTIMACION NETA SIN IVA
                if x.sub_total_esc > 0:
                    x.estimacion_subtotal = x.sub_total_esc_h
                else:
                    x.estimacion_subtotal = x.estimado - x.amort_anticipo
                x.estimacion_iva = (x.estimado - x.amort_anticipo) * x.b_iva # METODO PARA CALCULAR ESTIMACION IVA.
                x.estimacion_facturado = x.estimacion_subtotal + x.estimacion_iva # METODO PARA CALCULAR ESTIMACION + IVA

                datos_estimacion = {
                    'estimacion_iva': x.estimacion_iva, 'estimacion_facturado': x.estimacion_facturado,
                    'estimacion_subtotal': x.estimacion_subtotal, 'amort_anticipo': x.amort_anticipo,
                   'estimado_deducciones': estimado_deducciones
                }
                b_est.write(datos_estimacion)
                # IMPORTE LIQUIDO
                for rec in x:
                    if x.sancion > 0:
                        datos_pagar_ret1 = {
                            # SE RETIENE
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) - (
                            sancion) + x.devolucion_est - (x.ret_neta_est * -1)
                        }
                        b_est.write(datos_pagar_ret1)
                    elif x.retenido_anteriormente <= x.total_ret_est:
                        datos_pagar_ret = {
                            # SE RETIENE
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) - (x.ret_neta_est * -1)
                        }
                        b_est.write(datos_pagar_ret)
                    elif x.retenido_anteriormente > x.total_ret_est:
                        # SE DEVUELVE
                        datos_pagar_dev = {
                            'a_pagar': (x.estimacion_facturado - x.estimado_deducciones) + x.devolucion_est
                        }

                        b_est.write(datos_pagar_dev)'''





