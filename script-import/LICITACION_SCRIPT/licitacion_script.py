import odoorpc, csv
import datetime
import mysql.connector

import time


usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                            host='sidur.galartec.com',
                            database='sidur')
cursor = cnx.cursor(dictionary=True) 

query = ("SELECT * FROM `licitaciones` INNER JOIN licitacion_fechas ON licitaciones.num_licitacion = licitacion_fechas.id_licitacion INNER JOIN licitacion_datos_generales ON licitaciones.num_licitacion = licitacion_datos_generales.id_licitacion order by id desc;")

cursor.execute(query)

for row in cursor:
    print(row['id'])
    lici = odoo.env['proceso.licitacion']

    _search_lici = odoo.env['proceso.licitacion'].search(
        [("numerolicitacion", "=", row['num_licitacion'])])

    b_lici = lici.browse(_search_lici)

    if int(row['id']) != int(b_lici.id_sideop):
        print('YA EXISTE LICITACION')
    else:
        print('actualizar licitacion')

        # prog inv
        pinv = odoo.env['generales.programas_inversion']
        _search_pinv = odoo.env['generales.programas_inversion'].search(
            [("id_sideop", "=", row['id_prog_inv'])])
        b_pinv = pinv.browse(_search_pinv)
        print(b_pinv)

        '''user = odoo.env['res.users']
        _search_user = odoo.env['res.users'].search(
            [("name", "=", row['nombre_preside'])])
        b_user = user.browse(_search_user)
        print(b_user.name)'''
        #fechas
        if len(str(row['fecha_conv'])) < 10:
            fecha_conv = None
        else:
            fecha_conv_ = str(row['fecha_conv'])
            fecha_conv = fecha_conv_[6] + fecha_conv_[7] + fecha_conv_[8] + fecha_conv_[9] + fecha_conv_[
                5] + fecha_conv_[3] + fecha_conv_[4] + fecha_conv_[2] + fecha_conv_[0] + fecha_conv_[1]

        if len(str(row['fecha_compranet'])) < 10:
            fecha_compranet = None
        else:
            fecha_compranet_ = str(row['fecha_compranet'])
            fecha_compranet = fecha_compranet_[6] + fecha_compranet_[7] + fecha_compranet_[8] + fecha_compranet_[9] + fecha_compranet_[
                5] + fecha_compranet_[3] + fecha_compranet_[4] + fecha_compranet_[2] + fecha_compranet_[0] + fecha_compranet_[1]
        
        print(row['fecha_visita'])

        if len(str(row['fecha_visita'])) < 10:
            fecha_visita = None
        #trampa
        elif str(row['fecha_visita']) == '00/00/2017':
            fecha_visita = None
        elif str(row['fecha_visita']) == '00/00/2018':
            fecha_visita = None
        elif str(row['fecha_visita']) == '00/00/2019':
            fecha_visita = None
        elif str(row['fecha_visita']) == '00/00/0000':
            fecha_visita = None
        elif str(row['fecha_visita']) == '00/00/2000':
            fecha_visita = None
        else:
            fecha_visita_ = str(row['fecha_visita'])
            fecha_visita = fecha_visita_[6] + fecha_visita_[7] + fecha_visita_[8] + fecha_visita_[9] + fecha_visita_[
                5] + fecha_visita_[3] + fecha_visita_[4] + fecha_visita_[2] + fecha_visita_[0] + fecha_visita_[1]

        if len(str(row['fecha_junta'])) < 10:
            fecha_junta = None
        else:
            fecha_junta_ = str(row['fecha_junta'])
            fecha_junta = fecha_junta_[6] + fecha_junta_[7] + fecha_junta_[8] + fecha_junta_[9] + fecha_junta_[
                5] + fecha_junta_[3] + fecha_junta_[4] + fecha_junta_[2] + fecha_junta_[0] + fecha_junta_[1]

        if len(str(row['fecha_apertura'])) < 10:
            fecha_apertura = None
        else:
            fecha_apertura_ = str(row['fecha_apertura'])
            fecha_apertura = fecha_apertura_[6] + fecha_apertura_[7] + fecha_apertura_[8] + fecha_apertura_[9] + fecha_apertura_[
                5] + fecha_apertura_[3] + fecha_apertura_[4] + fecha_apertura_[2] + fecha_apertura_[0] + fecha_apertura_[1]

        if len(str(row['fecha_fallo'])) < 10:
            fecha_fallo = None
        else:
            fecha_fallo_ = str(row['fecha_fallo'])
            fecha_fallo = fecha_fallo_[6] + fecha_fallo_[7] + fecha_fallo_[8] + fecha_fallo_[9] + fecha_fallo_[
                5] + fecha_fallo_[3] + fecha_fallo_[4] + fecha_fallo_[2] + fecha_fallo_[0] + fecha_fallo_[1]

        if len(str(row['fecha_limit'])) < 10:
            fecha_limit = None
        else:
            fecha_limit_ = str(row['fecha_limit'])
            fecha_limit = fecha_limit_[6] + fecha_limit_[7] + fecha_limit_[8] + fecha_limit_[9] + fecha_limit_[
                5] + fecha_limit_[3] + fecha_limit_[4] + fecha_limit_[2] + fecha_limit_[0] + fecha_limit_[1]

        if len(str(row['fecha_estimada_inicio'])) < 10:
            fecha_estimada_inicio = None
        else:
            fecha_estimada_inicio_ = str(row['fecha_estimada_inicio'])
            fecha_estimada_inicio = fecha_estimada_inicio_[6] + fecha_estimada_inicio_[7] + fecha_estimada_inicio_[8] + fecha_estimada_inicio_[9] + fecha_estimada_inicio_[
                5] + fecha_estimada_inicio_[3] + fecha_estimada_inicio_[4] + fecha_estimada_inicio_[2] + fecha_estimada_inicio_[0] + fecha_estimada_inicio_[1]

        if len(str(row['fecha_estimada_final'])) < 10:
            fecha_estimada_final = None
        else:
            fecha_estimada_final_ = str(row['fecha_estimada_final'])
            fecha_estimada_final = fecha_estimada_final_[6] + fecha_estimada_final_[7] + fecha_estimada_final_[8] + fecha_estimada_final_[9] + fecha_estimada_final_[
                5] + fecha_estimada_final_[3] + fecha_estimada_final_[4] + fecha_estimada_final_[2] + fecha_estimada_final_[0] + fecha_estimada_final_[1]


        if len(str(row['fecha_oficio_preside'])) < 10:
            fecha_oficio_preside = None
        else:
            fecha_oficio_preside_ = str(row['fecha_oficio_preside'])
            fecha_oficio_preside = fecha_oficio_preside_[6] + fecha_oficio_preside_[7] + fecha_oficio_preside_[8] + fecha_oficio_preside_[9] + fecha_oficio_preside_[
                5] + fecha_oficio_preside_[3] + fecha_oficio_preside_[4] + fecha_oficio_preside_[2] + fecha_oficio_preside_[0] + fecha_oficio_preside_[1]

        if len(str(row['fecha_oficio_contraloria'])) < 10:
            fecha_oficio_contraloria = None
        else:
            fecha_oficio_contraloria_ = str(row['fecha_oficio_contraloria'])
            fecha_oficio_contraloria = fecha_oficio_contraloria_[6] + fecha_oficio_contraloria_[7] + fecha_oficio_contraloria_[8] + fecha_oficio_contraloria_[9] + fecha_oficio_contraloria_[
                5] + fecha_oficio_contraloria_[3] + fecha_oficio_contraloria_[4] + fecha_oficio_contraloria_[2] + fecha_oficio_contraloria_[0] + fecha_oficio_contraloria_[1]

        tipo = ''
        # tipo licitacion
        if str(row['tipo_licitacion']) == "LN":
            tipo = '1'
        elif str(row['tipo_licitacion']) == "IR":
            tipo = '2'

        print('tipo', tipo)
        print(row['num_licitacion'])
        datos_lici = {
            # 'id_sideop': row['id'],
            # 'tipolicitacion': tipo,

            # 'programa_inversion_licitacion': b_pinv.id,
            # 'numerolicitacion': row['num_licitacion'],
            # 'name': row['descripcion'],
            # 'convocatoria': row['convocatoria'],
            # 'fechaconinv': fecha_conv,

            # 'caracter': row['caracter'],
            # 'normatividad': row['normatividad'],
            # 'id_sideop_partida': row['fun_responsable'],
            # 'id_sideop_partida': row['fecha'],

            # 'id_sideop_partida': row['descripcion'],
            # 'id_sideop_partida': row['status'],
            # 'id_sideop_partida': row['fecha_can_des'],
            # 'id_sideop_partida': row['coment_can_des'],
            # 'puntosminimospropuestatecnica': row['min_puntos'],
            # 'fecharegistrocompranet': row['fecha_creacion'],
            # 'fecharegistrocompranet': fecha_compranet,

            # 'visitafechahora': fecha_visita,
            # 'visitalugar': row['lugar_visita'],
            # 'juntafechahora': fecha_junta,
            # 'juntalugar': row['lugar_junta'],
            # 'aperturafechahora': fecha_apertura,
            # 'aperturalugar': row['lugar_apertura'],
            # 'fallofechahora': fecha_fallo,
            # 'fallolugar': row['lugar_fallo'],

            # 'fechalimiteentregabases': fecha_limit,
            # 'costobasesdependencia': row['costo_bases'],
            # 'costocompranetbanco': row['costo_compranet'],
            # 'fechaestimadainicio': fecha_estimada_inicio,
            # 'fechaestimadatermino': fecha_estimada_final,
            # 'id_sideop_partida': row['plazo_dias'],
            # 'capitalcontable': row['cap_contable'],
            # 'anticipomaterial': float(row['anticipo_mat']),
            # 'anticipoinicio': float(row['anticipo_ini']),

            # 'puesto': row['nombre_preside'],
            # 'puesto': row['puesto_preside'],
            # 'numerooficio': row['oficio_preside'],
            # 'fechaoficio': fecha_oficio_preside,
            # 'fechaoficio2': fecha_oficio_contraloria,
            # 'oficioinvitacioncontraloria': row['oficio_contraloria'],
            # 'notariopublico': row['notario'],

        }


        if len(str(row['fecha_can_des'])) < 10:
            fecha_can_des = None
        else:
            fecha_can_des_ = str(row['fecha_can_des'])
            fecha_can_des = fecha_can_des_[6] + fecha_can_des_[7] + fecha_can_des_[8] + fecha_can_des_[9] + fecha_can_des_[
                5] + fecha_can_des_[3] + fecha_can_des_[4] + fecha_can_des_[2] + fecha_can_des_[0] + fecha_can_des_[1]

        # licitacion = b_lici.write(datos_lici)
        # 999 = cancelar
        if str(row['status']) == '999':
            print(' yees ------')
            lici_ca = odoo.env['proceso.estado_obra_cancelar']
            estatus = 'Cancelada'
            datos_est = {
                'numerolicitacion': b_lici.id,
                'estado_obra_cancelar': estatus,
                'fecha_cancelado': fecha_can_des,
                'observaciones_cancelado': row['coment_can_des'],

            }
            sss = odoo.env['proceso.estado_obra_cancelar'].search_count(
                [("numerolicitacion", "=", b_lici.id)])
            if sss >= 1:
                pass
            else:
                licitacion_ca = lici_ca.create(datos_est)
        elif str(row['status']) == '998':
            print(' yees --x----')
            lici_ca = odoo.env['proceso.estado_obra_desierta']
            estatus = 'Desierta'
            datos_est = {
                'numerolicitacion': b_lici.id,
                'estado_obra_cancelar': estatus,
                'fecha_desierta': fecha_can_des,
                'observaciones_desierta': row['coment_can_des'],
            }
            sss = odoo.env['proceso.estado_obra_desierta'].search_count(
                [("numerolicitacion", "=", b_lici.id)])
            if sss >= 1:
                pass
            else:
                licitacion_ca = lici_ca.create(datos_est)
        else:
            pass
        print('exito')

    '''if row['tipo_procedimiento'] == "AD":
        tipo_contrato = "2"  # 2 es para adjudicacion

        _search_contrato = odoo.env['proceso.elaboracion_contrato'].search_count(
            [("contrato", "=", row['numero_contrato'])])
        if _search_contrato == 0:

            #crear contrato

            #tomar en cuenta el contratista_sideop
            _search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search(
                [("numerocontrato", "=", row['referencia'])], limit=1)

            try:
                adjudicacion = _search_adjudicacion[0]
            except:
                print("error al buscar contrato" + str(row['num_contrato']))

            datos_contrato = {
                'tipo_contrato': tipo_contrato,
                'adjudicacion': adjudicacion,
                'contrato': row['numero_contrato'],
                'num_contrato_sideop': row['num_contrato'],
                'id_contratista': row['id_contratista'],
                'id_residente': row['id_residente'],
                'name': row['objecto'],
                'unidadresponsableejecucion.id': row['unidad_responsable'],

                'periodicidadretencion': row['periodo_retencion'],
                'retencion': row['porcentaje_retencion'],
                'id_sideop_partida': row['id_partida'],

            }

            contrato = odoo.env['proceso.elaboracion_contrato']
            id_contrato = contrato.create(datos_contrato)

            contrato_id = contrato.browse(id_contrato)

            #Crear partida de esta misma linea
            datos_partida = {         # 'obra': str(partidas.obra.id),
                'contrato_partida_adjudicacion': [[0, 0, {'id_contrato_sideop': row['num_contrato']
                                                             ,'id_contratista': row['id_contratista']
                                                             ,'id_partida': row['id_partida']
                                                             ,'programaInversion.id': row['programa'],
                                                              'monto_partida': row['importe'],
                                                              'nombre_partida': str(id_contrato),
                                                              'id_contrato_relacion': str(adjudicacion),
                                                              'p_id': str(1)
                                                              }]]
            }
            
            partida_al_contrato = contrato_id.write(datos_partida)
        else:

            _search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search(
                [("numerocontrato", "=", row['referencia'])], limit=1)'''

