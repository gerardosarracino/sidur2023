import odoorpc, csv
import datetime
import mysql.connector
from datetime import datetime
import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                            host='sidur.galartec.com',
                            database='sidur') 
cursor = cnx.cursor(dictionary=True) 

query = (
    "SELECT * FROM `soavancesgeneral` where num_contrato = 'SIDUR-PF-18-245.1494' order by Id asc;")  # INNER JOIN soavances ON soavancesgeneral.id = soavancesgeneral.id_concepto
# where sorutacritica.Id > 2278 SELECT soav.num_contrato, soav.NumeroAvance, soav.FechaAvance, soav.SituacionContrato, soav.ComentarioAvance, soav.ComentarioGral, soav.Id AS idGeneral, soav.AvFis, soar.* FROM `soavancesgeneral` soav INNER JOIN sorutacritica soar ON soav.num_contrato = soar.num_contrato order by soar.Id asc
cursor.execute(query)
# where Id > 12696  where num_contrato = 'SIDUR-PF-15-086.30'  where Id > 470 SIDUR-ED.-18-278.1551 where Id = 'SIDUR-ED-20-002.1873'
# esta consulta sera para insertar los conceptos dentro de ruta_critica SELECT soav.num_contrato, soav.NumeroAvance, soav.IdActividad, soav.Id AS idGeneral, soav.PorcentajeReal, soar.* FROM `soavances` soav INNER JOIN sorutacritica soar ON soav.IdActividad = soar.Id order by soar.Id asc
for row in cursor:
    print('LA ID ES xx', row['Id'], 'y el contrato es x',row['num_contrato'], row['AvFis']) 

    # EN SIDEOP ESTA MAL ESCRITO, TIENE PUNTO EN VEZ DE GUION
    if str(row['num_contrato']) == 'SIDUR-ED.-18-278.1551':
        numC = 'SIDUR-ED-18-278.1551'
    else:
        numC = row['num_contrato']

    numero_contrato_id = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", numC)])
    # CONTAR SI EXISTE LA PARTIDA PARA PODER PROSEGUIR
    '''buscar_partida = odoo.env['partidas.partidas'].search_count(
        [("id_contrato_sideop", "=", row['num_contrato'])])'''

    # Buscamos en informe de avance
    buscar_informe_avance = odoo.env['proceso.iavance'].search_count(
        [("num_contrato", "=", row['num_contrato']), ("num_avance", "=", row['NumeroAvance'])])

    buscar_informe_update = odoo.env['proceso.iavance'].search_count(
    [("id_sideop", "=", row['Id'])])

    if buscar_informe_update != 0:
        print('AGREGAR Y ACTUALIZAR')

        avance = odoo.env['proceso.iavance']
        programa = odoo.env['programa.programa_obra']
        estimacion = odoo.env['control.estimaciones']
        fecha_act = (str(row['FechaAvance']))

        if str(row['SituacionContrato']) == '1':
            situacion = 'bien'
        elif str(row['SituacionContrato']) == '2':
            situacion = 'satisfactorio'
        elif str(row['SituacionContrato']) == '3':
            situacion = 'regular'
        elif str(row['SituacionContrato']) == '4':
            situacion = 'deficiente'
        elif str(row['SituacionContrato']) == '5':
            situacion = 'mal'

        b_programa = odoo.env['programa.programa_obra'].search([('obra.id', '=', numero_contrato_id)])

        b_prog = programa.browse(b_programa)

        date_format = "%Y/%m/%d"
        date_format2 = "%Y-%m-%d"
        hoy = str(fecha_act)

        if len(hoy) == '':
            print('1')
            Prog_Del = None
        else:
            Prog_Del_ = str(hoy)
            Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

        fecha_hoy = datetime.strptime(str(Prog_Del), date_format)

        if b_prog.fecha_termino_convenida is not False:
            fecha_termino_pp = b_prog.fecha_termino_convenida
        else:
            fecha_termino_pp = b_prog.fecha_termino_programa

        fecha_termino_contrato = datetime.strptime(str(fecha_termino_pp), date_format2)

        acumulado = 0
        cont = 0
        acumulado2 = 0
        porcentajeProgramado = 0
        porcentajefinanciero = 0

        if str(b_prog.programa_contratos) == "Recordset('proceso.programa', [])":
            print(
                ';SJAJSAJJ JOTO'
            )
            porcentajeProgramado = 0
            porcentajefinanciero = 0
        else:
            print('----')

            for i in b_prog.programa_contratos:
                cont += 1
                fecha_termino_p = datetime(i.fecha_termino.year, i.fecha_termino.month, i.fecha_termino.day)
                fechahoy = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)

                if fecha_hoy > fecha_termino_contrato:
                    porcentajeProgramado = 100.00
                # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                if fecha_hoy <= fecha_termino_contrato:
                    # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                    if str(fecha_termino_p) <= str(fechahoy):
                        # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                        fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                        fecha_actual = datetime.strptime(str(Prog_Del), date_format)
                        r = fecha_actual - fechainicioprog
                        dias_trans = r.days + 1
                        # print(dias_trans)
                        # DIAS DEL MES DEL PROGRAMA ACTUAL
                        dia_mes_inicio = datetime.strptime(str(i.fecha_inicio), date_format2)
                        # print(dia_mes_inicio)
                        dia_mes_termino = datetime.strptime(str(i.fecha_termino), date_format2)
                        # print(dia_mes_termino)
                        r2 = dia_mes_termino - dia_mes_inicio
                        dias_del_mes = r2.days + 1

                        if dias_del_mes == 0:
                            dias_del_mes = 1
                        # print(dias_del_mes)
                        # MONTO ACUMULADO DE PROGRAMAS
                        acumulado += i.monto

                        if str(cont) == '1':
                            ultimo_monto = 0
                        else:
                            ultimo_monto = i.monto

                        # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                        # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                        # EL TOTAL DEL PROGRAMA * 100
                        
                        if str(i.monto) == '0.0': 
                            monto_ = 1
                        else:
                            monto_ = i.monto
                        importe_diario = ((((monto_ / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto)) /
                                        b_prog.total_programa) * 100

                        # print(monto_, '------------',(((monto_ / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto)), '=-----', b_prog.total_programa)

                        if importe_diario > 100:
                            rr = 100
                        elif importe_diario <= 100:
                            rr = importe_diario
        
                        porcentajeProgramado = rr
                    else:
                        pass
        

        b_est = odoo.env['control.estimaciones'].search([('obra.id', '=', numero_contrato_id)])
        acumr = 0
        fin = 0
        for o in b_est:
            b_estt = estimacion.browse(o)
            # xdd = datetime.strptime(str(b_estt.fecha_termino_estimacion), date_format2)
            fecha_actx_ = str(fecha_act)
            
            fecha_actx = fecha_actx_[0] + fecha_actx_[1] + fecha_actx_[2] + fecha_actx_[3] + \
                            '-' + fecha_actx_[4] + fecha_actx_[5] + '-' + \
                            fecha_actx_[6] + fecha_actx_[7]
            kk = b_estt.fecha_inicio_estimacion
            kk2 = datetime.strptime(str(fecha_actx), date_format2)
            xdd = datetime(kk2.year, kk2.month, kk2.day)
            xdd2 = datetime(kk.year, kk.month, kk.day)

            for x in b_estt:
                if xdd < xdd2:
                    pass
                else:
                    acumr += x.estimado
                    fin = (acumr / b_prog.total_programa) * 100  
                    
                    porcentajefinanciero = fin
        
        campos_ia = {
                    # 'porcentajeProgramado': porcentajeProgramado,
                    # 'porcentaje_estimado': row['AvFis'],

                     'avance_financiero': float(porcentajefinanciero),
                    #  'situacion_contrato': situacion,
                    #  'fecha_actual': str(fecha_act),
                    #  'com_avance_obra': str(row['ComentarioAvance']),
                    #  'comentarios_generales': str(row['ComentarioGral']),
                    #  'numero_contrato': numero_contrato_id[0],
                    #  'num_contrato': str(row['num_contrato']),
                    #  'id_sideop': row['Id'],
                    #  'num_avance': row['NumeroAvance'],
                     } 

        buscar_informe_avancew = odoo.env['proceso.iavance'].search(
        [("numero_contrato", "=", numero_contrato_id), ("fecha_actual", "=", str(fecha_act))])

        b_ia = avance.browse(buscar_informe_avancew)
        # form_ia = avance.create(campos_ia)
        print('EXITO')
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', fecha_act, 'xxxxxxxxxx', porcentajefinanciero)
        form_ia = b_ia.write(campos_ia)

    else:
        print(' YA EXISTEN')

    '''print(buscar_informe_avance)
    if buscar_informe_avance == 0:

        print('NO EXISTE EL INFORME, CREAR DATOS DE INFORME')

        avance = odoo.env['proceso.iavance']
        programa = odoo.env['programa.programa_obra']
        estimacion = odoo.env['control.estimaciones']
        fecha_act = (str(row['FechaAvance']))

        if str(row['SituacionContrato']) == '1':
            situacion = 'bien'
        elif str(row['SituacionContrato']) == '2':
            situacion = 'satisfactorio'
        elif str(row['SituacionContrato']) == '3':
            situacion = 'regular'
        elif str(row['SituacionContrato']) == '4':
            situacion = 'deficiente'
        elif str(row['SituacionContrato']) == '5':
            situacion = 'mal'

        b_programa = odoo.env['programa.programa_obra'].search([('obra.id', '=', numero_contrato_id)])

        b_prog = programa.browse(b_programa)
        

        date_format = "%Y/%m/%d"
        date_format2 = "%Y-%m-%d"
        hoy = str(fecha_act)

        if len(hoy) == '':
            print('1')
            Prog_Del = None
        else:
            Prog_Del_ = str(hoy)
            Prog_Del = Prog_Del_[0] + Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3] + '/' + Prog_Del_[4] + Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7]

        fecha_hoy = datetime.strptime(str(Prog_Del), date_format)

        if b_prog.fecha_termino_convenida is not False:
            fecha_termino_pp = b_prog.fecha_termino_convenida
        else:
            fecha_termino_pp = b_prog.fecha_termino_programa

        fecha_termino_contrato = datetime.strptime(str(fecha_termino_pp), date_format2)

        acumulado = 0
        cont = 0
        acumulado2 = 0
        porcentajeProgramado = 0
        porcentajefinanciero = 0
        for i in b_prog.programa_contratos:
            cont += 1
            fecha_termino_p = datetime(i.fecha_termino.year, i.fecha_termino.month, i.fecha_termino.day)
            fechahoy = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)

            if fecha_hoy > fecha_termino_contrato:
                porcentajeProgramado = 100.00
            # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
            if fecha_hoy <= fecha_termino_contrato:
                # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                if str(fecha_termino_p) <= str(fechahoy):
                    # DIAS TRANSCURRIDOS DESDE EL INICIO DEL PROGRAMA ACTUAL HASTA LA FECHA ACTUAL
                    fechainicioprog = datetime.strptime(str(i.fecha_inicio), date_format2)
                    fecha_actual = datetime.strptime(str(Prog_Del), date_format)
                    r = fecha_actual - fechainicioprog
                    dias_trans = r.days + 1
                    # print(dias_trans)
                    # DIAS DEL MES DEL PROGRAMA ACTUAL
                    dia_mes_inicio = datetime.strptime(str(i.fecha_inicio), date_format2)
                    # print(dia_mes_inicio)
                    dia_mes_termino = datetime.strptime(str(i.fecha_termino), date_format2)
                    # print(dia_mes_termino)
                    r2 = dia_mes_termino - dia_mes_inicio
                    dias_del_mes = r2.days + 1

                    if dias_del_mes == 0:
                        dias_del_mes = 1
                    # print(dias_del_mes)
                    # MONTO ACUMULADO DE PROGRAMAS
                    acumulado += i.monto

                    if str(cont) == '1':
                        ultimo_monto = 0
                    else:
                        ultimo_monto = i.monto

                    # LA FORMULA ES: MONTO DEL PROGRAMA ACTUAL / LOS DIAS DEL MES DEL PROGRAMA ACTUAL *
                    # LOS DIAS TRANSCURRIDOS HASTA LA FECHA ACTUAL + EL ACUMULADO DE LOS PROGRAMAS /
                    # EL TOTAL DEL PROGRAMA * 100
                    importe_diario = ((((i.monto / dias_del_mes) * dias_trans) + (acumulado - ultimo_monto)) /
                                      b_prog.total_programa) * 100

                    porcentajeProgramado = importe_diario
                else:
                    pass'''
    '''b_estimaciones = odoo.env['control.estimaciones'].search([('obra.id', '=', numero_contrato_id)])
        
        print(b_estimaciones)
        for i in b_estimaciones:
            print('xd')
            b_est = estimacion.browse(i)
            for i in b_est:
                fecha_termino_e = datetime(i.fecha_termino_estimacion.year, i.fecha_termino_estimacion.month, i.fecha_termino_estimacion.day)
                fechahoye = datetime(fecha_hoy.year, fecha_hoy.month, fecha_hoy.day)

                # SI LA FECHA ACTUAL ES MAYOT A LA DEL TERMINO DEL CONTRATO ENTONCES EL PORCENTAJE PROGRAMADO DEBERIA
                # DE SER 100
                if fecha_hoy > fecha_termino_contrato:
                    porcentajefinanciero = 100
                # SI NO, LA FECHA DE HOY ES MENOR O IGUAL A LA DEL TERMINO DEL CONTRATO ENTONCES CALCULAR PORCENTAJE
                if fecha_hoy <= fecha_termino_contrato:
                    # POSICIONARSE EN EL PROGRAMA CORRESPONDIENTE DE LA FECHA ACTUAL (MISMO MES Y ANO)
                    if str(fecha_termino_e) <= str(fechahoye):
                        acumulado2 += i.estimado

                        if str(b_est.idobra) == '1':
                            ultimo_monto = 0
                        else:
                            ultimo_monto = i.estimado

                        # print(acumulado2, 'xxxxxxxxxxxxxxxxxxxxxxxxxx')

                        importe_diario = ((acumulado2 - ultimo_monto) /
                                        b_prog.total_partida) * 100

                        porcentajefinanciero = importe_diario
                    else:
                        pass
'''
    '''campos_ia = {
                    'porcentajeProgramado': porcentajeProgramado,
                    'porcentaje_estimado': row['AvFis'],

                    'avance_financiero': porcentajefinanciero,
                     'situacion_contrato': situacion,
                     'fecha_actual': str(fecha_act),
                     'com_avance_obra': str(row['ComentarioAvance']),
                     'comentarios_generales': str(row['ComentarioGral']),
                     'numero_contrato': numero_contrato_id[0],
                     'num_contrato': str(row['num_contrato']),
                     'id_sideop': row['Id'],
                     'num_avance': row['NumeroAvance'],
                     } 

        buscar_informe_avancew = odoo.env['proceso.iavance'].search(
        [("numero_contrato", "=", numero_contrato_id), ("num_avance", "=", row['NumeroAvance'])])

        b_ia = avance.browse(buscar_informe_avancew)
        form_ia = avance.create(campos_ia)
        # form_ia = b_ia.write(campos_ia)
    else:
        print('YA EXISTE WTFFFFFF')'''