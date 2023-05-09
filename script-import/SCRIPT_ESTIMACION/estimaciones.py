import odoorpc, csv
import datetime
import mysql.connector

import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='Navojoa2020',
                            host='sidur.galartec.com',
                            database='sideop') 
cursor = cnx.cursor(dictionary=True) 

query = ("SELECT * FROM `estimaciones` where num_contrato = 'SIDUR-ED-19-196.1846' order by estimaciones.id asc;") # where estimaciones.id > 6690 order by estimaciones.id asc; where num_contrato = 'SIDUR-PF-18-287.1577'

cursor.execute(query)

for row in cursor:

    print('el contrato es ', row['num_contrato'], ' y la id es ', row['id'])

    contratox = odoo.env['partidas.partidas']

    _search_contratox = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

    b_contratox = contratox.browse(_search_contratox)

    '''_search_part = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", row['num_contrato'])])'''

    # _search_estimacion = odoo.env['control.estimaciones'].search_count([("obra", "=", b_contratox.id)])

    # _search_programa2 = odoo.env['programa.programa_obra'].search([("obra", "=", _search_part)])

    _search_programa2 = odoo.env['control.estimaciones'].search_count(
    [("idobra", "=", row['numEstimacion']), ("tipo_estimacion", "=", row['tipoEstimacion'])])
    # ("id_sideop", "=", row['id']),
    estimacion_ids = int(row['numEstimacion']) - 1

    estimaciones = odoo.env['control.estimaciones']

    _search_est = odoo.env['control.estimaciones'].search(
    [("id_sideop", "=", row['id']), ("idobra", "=", row['numEstimacion']), ("tipo_estimacion", "=", row['tipoEstimacion'])])

    b_est = estimaciones.browse(_search_est)

    # print('el contrato deberia de ser el ', b_est.obra.numero_contrato.contrato)

    # if _search_programa2 == 0:
    #     print('NO EXISTE ESE CONTRATO xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', row['num_contrato'])

    # else:
    #     _search_programa3 = odoo.env['partidas.partidas'].search(
    #         [("id_contrato_sideop", "=", row['num_contrato'])])


        # part_prog = _search_programa3[0]

    if str(_search_programa2) == '0':
        print('no existe crear estimacion -------x-------------x------------x------------')

        if str(row['tipoEstimacion']) == '2':

            '''try:
                part_prog = _search_programa3[0]
                # obra_partida = _search_programa2.obra
            except:
                print("error al buscar contrato" + str(row['num_contrato']))
                pass'''

            print('es escalatoria')

            fecha_inicial_ = str(row['fechaInicial'])
            fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + \
                            fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + \
                            fecha_inicial_[0] + fecha_inicial_[1]

            fecha_final_ = str(row['fechaFinal'])
            fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[
                5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

            fecha_presentacion_ = str(row['fechaPresentacion'])
            if str(row['fechaPresentacion']) == "":
                fecha_presentacion = None
            else:
                fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                    fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                    fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + \
                                    fecha_presentacion_[1]

            fecha_revision_ = str(row['fechaRevisionResidente'])
            if str(row['fechaRevisionResidente']) == "":
                fecha_revision = None
            else:
                fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[
                    9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + \
                                fecha_revision_[0] + fecha_revision_[1]

            _search_est_esca = odoo.env['control.estimaciones'].search(
                [("obra.id", "=", b_est.obra.id), ("idobra", "=", row['numEstimacion']), ("tipo_estimacion", "=", 1)])
            b_escalatoria = estimaciones.browse(_search_est_esca)

            if str(row['masRetencion_uno']) == '0.00':
                retencion = row['menosRetencion_uno']
            elif str(row['menosRetencion_uno']) == '0.00': # str(row['menosRetencion_uno']) == '0':
                retencion = row['masRetencion_uno']
            
            subtotal_est = float(row['ejecutado']) - float(row['amortizacionAnt'])

            datos_est = {
                'obra': b_contratox.id,
                'id_sideop': row['id'],
                'num_contrato': row['num_contrato'],
                'tipo_estimacion': str(row['tipoEstimacion']),
                # 'idobra': str(row['numEstimacion']),
                'fecha_inicio_estimacion': fecha_inicial,
                'fecha_termino_estimacion': fecha_final,
                'fecha_presentacion': fecha_presentacion,
                'fecha_revision': fecha_revision,
                'estimacion_ids': str(estimacion_ids),
                'amort_anticipo': float(row['amortizacionAnt']),
                'sub_total_esc_h': float(row['ejecutado']),
                'estimacion_subtotal': subtotal_est,
                'estimacion_iva': str(row['iva']),
                'estimacion_facturado': str(row['facturado']),
                'a_pagar': float(row['netoAPagar']),
                'notas': str(row['notas']),
                'amort_anticipo_partida': float(b_contratox.porcentaje_anticipo) + float(b_contratox.anticipo_material),
                'ret_neta_est': float(retencion),
                'estimado': float(row['ejecutado']),
            }
            # estimacion = b_est.write(datos_est)
            estimacion = estimaciones.create(datos_est)

            print('EXITO')
        else:
            '''try:
                part_prog = _search_programa3[0]
                # obra_partida = _search_programa2.obra
            except:
                print("error al buscar contrato" + str(row['num_contrato']))
                pass'''

            fecha_inicial_ = str(row['fechaInicial'])
            fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + fecha_inicial_[0] + fecha_inicial_[1]

            fecha_final_ = str(row['fechaFinal'])
            fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

            fecha_presentacion_ = str(row['fechaPresentacion'])
            
            if len(str(row['fechaPresentacion'])) < 10:
                fecha_presentacion = None
            else:
                fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                    fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                    fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + fecha_presentacion_[1]

            fecha_revision_ = str(row['fechaRevisionResidente'])
            if str(row['fechaRevisionResidente']) == "":

                fecha_revision = None
            elif str(row['fechaRevisionResidente']) == "17/0082016":
                fecha_revision = "2016/08/17"
            else:
                fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + fecha_revision_[0] + fecha_revision_[1]

            if str(row['masRetencion_uno']) == '0.00':
                retencion = row['menosRetencion_uno']
            elif str(row['menosRetencion_uno']) == '0.00': # str(row['menosRetencion_uno']) == '0':
                retencion = row['masRetencion_uno']
            
            subtotal_est = float(row['ejecutado']) - float(row['amortizacionAnt'])

            datos_est = {
                'obra': b_contratox.id,
                'id_sideop': str(row['id']),
                'num_contrato': str(row['num_contrato']),
                'tipo_estimacion': str(row['tipoEstimacion']),
                'fecha_inicio_estimacion': fecha_inicial,
                'fecha_termino_estimacion': fecha_final,
                'fecha_presentacion': fecha_presentacion,
                'fecha_revision': fecha_revision,
                'estimacion_ids': str(estimacion_ids),
                'amort_anticipo': float(row['amortizacionAnt']),
                'sub_total_esc_h': float(row['ejecutado']),
                'estimacion_subtotal': subtotal_est,
                'estimacion_iva': str(row['iva']),
                'estimacion_facturado': str(row['facturado']),
                'a_pagar': float(row['netoAPagar']),
                'notas': str(row['notas']),
                'amort_anticipo_partida': float(b_contratox.porcentaje_anticipo) + float(b_contratox.anticipo_material),
                'ret_neta_est': float(retencion),
                'estimado': float(row['ejecutado']),
            }

            # estimacion = b_est.write(datos_est)
            estimacion2 = estimaciones.create(datos_est)

            print('Exito')
        
    else:
        print('ya existe estimacion')


        if str(row['tipoEstimacion']) == '2':

            '''try:
                part_prog = _search_programa3[0]
                # obra_partida = _search_programa2.obra
            except:
                print("error al buscar contrato" + str(row['num_contrato']))
                pass'''

            print('es escalatoria')

            fecha_inicial_ = str(row['fechaInicial'])
            fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + \
                            fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + \
                            fecha_inicial_[0] + fecha_inicial_[1]

            fecha_final_ = str(row['fechaFinal'])
            fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[
                5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

            fecha_presentacion_ = str(row['fechaPresentacion'])
            if str(row['fechaPresentacion']) == "":
                fecha_presentacion = None
            else:
                fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                    fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                    fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + \
                                    fecha_presentacion_[1]

            fecha_revision_ = str(row['fechaRevisionResidente'])
            if str(row['fechaRevisionResidente']) == "":
                fecha_revision = None
            else:
                fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[
                    9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + \
                                fecha_revision_[0] + fecha_revision_[1]

            _search_est_esca = odoo.env['control.estimaciones'].search(
                [("obra.id", "=", b_est.obra.id), ("idobra", "=", row['numEstimacion']), ("tipo_estimacion", "=", 1)])
            b_escalatoria = estimaciones.browse(_search_est_esca)

            if str(row['masRetencion_uno']) == '0.00':
                retencion = row['menosRetencion_uno']
            elif str(row['menosRetencion_uno']) == '0.00': # str(row['menosRetencion_uno']) == '0':
                retencion = row['masRetencion_uno']
            
            subtotal_est = float(row['ejecutado']) - float(row['amortizacionAnt'])
            
            datos_est = {
                'obra': b_contratox.id,
                'id_sideop': row['id'],
                'num_contrato': row['num_contrato'],
                'tipo_estimacion': str(row['tipoEstimacion']),
                # 'idobra': str(row['numEstimacion']),
                'fecha_inicio_estimacion': fecha_inicial,
                'fecha_termino_estimacion': fecha_final,
                'fecha_presentacion': fecha_presentacion,
                'fecha_revision': fecha_revision,
                'estimacion_ids': str(estimacion_ids),
                'amort_anticipo': float(row['amortizacionAnt']),
                'sub_total_esc_h': float(row['ejecutado']),
                'estimacion_subtotal': subtotal_est,
                'estimacion_iva': str(row['iva']),
                'estimacion_facturado': str(row['facturado']),
                'a_pagar': float(row['netoAPagar']),
                'notas': str(row['notas']),
                'amort_anticipo_partida': float(b_contratox.porcentaje_anticipo) + float(b_contratox.anticipo_material),
                'ret_neta_est': float(retencion),
                'estimado': float(row['ejecutado']),
            }
            estimacion = b_est.write(datos_est)
            # estimacion = estimaciones.create(datos_est)

            print('EXITO')
        else:
            '''try:
                part_prog = _search_programa3[0]
                # obra_partida = _search_programa2.obra
            except:
                print("error al buscar contrato" + str(row['num_contrato']))
                pass'''

            fecha_inicial_ = str(row['fechaInicial'])
            fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + fecha_inicial_[0] + fecha_inicial_[1]

            fecha_final_ = str(row['fechaFinal'])
            fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

            fecha_presentacion_ = str(row['fechaPresentacion'])
            
            if len(str(row['fechaPresentacion'])) < 10:
                fecha_presentacion = None
            else:
                fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                    fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                    fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + fecha_presentacion_[1]

            fecha_revision_ = str(row['fechaRevisionResidente'])
            if str(row['fechaRevisionResidente']) == "":

                fecha_revision = None
            elif str(row['fechaRevisionResidente']) == "17/0082016":
                fecha_revision = "2016/08/17"
            else:
                fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + fecha_revision_[0] + fecha_revision_[1]

            if str(row['masRetencion_uno']) == '0.00':
                retencion = row['menosRetencion_uno']
            elif str(row['menosRetencion_uno']) == '0.00': # str(row['menosRetencion_uno']) == '0':
                retencion = row['masRetencion_uno']
            
            print(retencion)

            subtotal_est = float(row['ejecutado']) - float(row['amortizacionAnt'])

            datos_est = {
                 'obra': b_contratox.id,
                 'id_sideop': str(row['id']),
                 'num_contrato': str(row['num_contrato']),
                 'tipo_estimacion': str(row['tipoEstimacion']),
                 'fecha_inicio_estimacion': fecha_inicial,
                 'fecha_termino_estimacion': fecha_final,
                 'fecha_presentacion': fecha_presentacion,
                 'fecha_revision': fecha_revision,
                 'estimacion_ids': str(estimacion_ids),
                 'amort_anticipo': float(row['amortizacionAnt']),
                 'sub_total_esc_h': float(row['ejecutado']),
                 'estimacion_subtotal': float(subtotal_est),
                 'estimacion_iva': str(row['iva']),
                 'estimacion_facturado': str(row['facturado']),
                'a_pagar': float(row['netoAPagar']),
                 'notas': str(row['notas']),
                 'amort_anticipo_partida': float(b_contratox.porcentaje_anticipo) + float(b_contratox.anticipo_material),
                'ret_neta_est': float(retencion),
                 'estimado': float(row['ejecutado']),
            }

            
            estimacion = b_est.write(datos_est)
            # estimacion2 = estimaciones.create(datos_est)

            print('Exito')

    