import odoorpc, csv
import datetime
import mysql.connector
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('35.223.0.35', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='35.223.0.35',
                              database='sideop_marzo')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `contratos` where numero_contrato = 'SIDUR-ED-20-006'") # WHERE tipo_procedimiento = 'LP'

cursor.execute(query)

for row in cursor:
    # BUSCAMOS LA EXISTENCIA DEL CONTRATO, SI NO EXISTE LO CREAMOS, SI YA EXISTE INSERTAMOS SU PARTIDA

    _search_contrato = odoo.env['proceso.elaboracion_contrato'].search_count(
            [("contrato", "=", row['numero_contrato'])])

    print('El contrato id es x', row['num_contrato'], ' y el contrato es x ', row['numero_contrato'], ' y su referencia es x ', row['referencia'])
    
    if row['tipo_procedimiento'] == "LP":

        if int(_search_contrato) == 0:
            print('crear')

            '''# tomar en cuenta el contratista_sideop
            licitacionx = odoo.env['proceso.licitacion']
            _search_lici = odoo.env['proceso.licitacion'].search(
                [("numerolicitacion", "=", row['referencia'])])
            b_lic = licitacionx.browse(_search_lici)

            # BUSQUEDA DEL CONTRATISTA
            c = odoo.env['contratista.contratista']
            _search_c = odoo.env['contratista.contratista'].search(
                [("id_sideop", "=", row['id_contratista'])])
            b_contra = c.browse(_search_c)

            # BUSQUEDA DE UNIDAD RESPONSABLE
            unidad = odoo.env['proceso.unidad_responsable']
            _search_unidad = odoo.env['proceso.unidad_responsable'].search(
                [("id_sideop", "=", row['unidad_responsable'])])
            b_unidad = unidad.browse(_search_unidad)

            # REFORMATEO DE FECHAS
            if len(str(row['fecha_inicio'])) < 10:
                fecha_inicio = None
            else:
                fecha_inicio_ = str(row['fecha_inicio'])
                fecha_inicio = fecha_inicio_[6] + fecha_inicio_[7] + fecha_inicio_[8] + \
                               fecha_inicio_[9] + fecha_inicio_[
                                   5] + fecha_inicio_[3] + fecha_inicio_[4] + fecha_inicio_[2] + \
                               fecha_inicio_[0] + fecha_inicio_[1]

            if len(str(row['fecha_termino'])) < 10:
                fecha_termino = None
            else:
                fecha_termino_ = str(row['fecha_termino'])
                fecha_termino = fecha_termino_[6] + fecha_termino_[7] + fecha_termino_[8] + \
                                fecha_termino_[9] + fecha_termino_[
                                    5] + fecha_termino_[3] + fecha_termino_[4] + fecha_termino_[2] + \
                                fecha_termino_[0] + fecha_termino_[1]

            if len(str(row['fecha'])) < 10:
                fecha = None
            else:
                fecha_ = str(row['fecha'])
                fecha = fecha_[6] + fecha_[7] + fecha_[8] + \
                        fecha_[9] + fecha_[
                            5] + fecha_[3] + fecha_[4] + fecha_[2] + \
                        fecha_[0] + fecha_[1]
            
            # BUSCAR ID PARA SUPERVISION EXTERNA SI APLICA
            s_externa = odoo.env['proceso.unidad_responsable']
            _search_externa = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['num_contrato'])])
            b_externa = s_externa.browse(_search_externa)

            datos_contrato = {
                'tipo_contrato': "1",
                'obra': b_lic.id,
                'adjudicacion': None,

                'contrato': row['numero_contrato'],

                # 'num_contrato_sideop': row['num_contrato'],

                'contratista': b_contra.id,
                # 'id_residente': row['id_residente'],
                'name': row['objecto'],
                'descripciontrabajos': row['trabajos'],
                'unidadresponsableejecucion': b_unidad.id,

                'periodicidadretencion': row['periodo_retencion'],
                'retencion': float(row['porcentaje_retencion']),
                # 'id_sideop_partida': row['id_partida'],
                'fechainicio': fecha_inicio,
                'fechatermino': fecha_termino,
                'fecha': fecha,
                'supervisionexterna': row['supervision_externa'],
                'supervisionexterna1': b_externa.id
                # 'nombre_partida': row['numero_contrato'],
            }
            contrato = odoo.env['proceso.elaboracion_contrato']

            id_contrato = contrato.create(datos_contrato)
            print('SE CREO EL CONTRATO DE LICITACION')

            contrato_id = contrato.browse(id_contrato)

            obraprogramada = odoo.env['registro.programarobra']
            _search_obra = odoo.env['registro.programarobra'].search([("Id_obraprogramada", "=", row['id_partida'])])
            b_obra = obraprogramada.browse(_search_obra)

            part_licitacion = odoo.env['partidas.licitacion']
            _search_partlic = odoo.env['partidas.licitacion'].search([("obra.id", "=", b_obra.id)])
            b_partlic = part_licitacion.browse(_search_partlic)

            

            # Crear partida de esta misma linea
            datos_partida = {  # 
                'contrato_partida_licitacion': [[0, 0, {
                                        'id_contrato_sideop': row['num_contrato']
                                        , 'id_contratista': b_contra.id
                                        # , 'id_partida': row['id_partida'],
                                        , 'obra': b_obra.id
                                        ,'recursos': b_partlic.recursos.id
                                        , 'programaInversion': b_partlic.programaInversion.id,
                                        'numero_contrato': contrato_id.id,
                                        'monto_partida': row['importe'],
                                        'iva_partida': row['iva_total'],
                                        'total_partida': row['total'],
                                        'id_contrato_relacion': str(contrato_id.obra.id),
                                        'p_id': int(id_contrato),
                                        'nombre_partida': row['num_contrato'],
                                        'nombre_contrato': row['numero_contrato'],
                                         }]]
            }
            
            # partida_al_contrato = contrato_id.write(datos_partida)

            print('EXITO AL CREAR CONTRATO DE LICITACION Y SU PRIMERA PARTIDA')'''

        else:
            print(' Ya existe este contrato asi que hay que insertar su partida')

            contra = odoo.env['proceso.elaboracion_contrato']
            _search_contratox = odoo.env['proceso.elaboracion_contrato'].search(
                [("contrato", "=", row['numero_contrato'])])
            b_contrato = contra.browse(_search_contratox)

            # _search_lici = odoo.env['proceso.licitacion'].search([("numerocontrato", "=", row['referencia'])])

            obraprogramada = odoo.env['registro.programarobra']
            _search_obra = odoo.env['registro.programarobra'].search([("Id_obraprogramada", "=", row['id_partida'])])
            b_obra = obraprogramada.browse(_search_obra)

            part_licitacion = odoo.env['partidas.licitacion']
            _search_partlic = odoo.env['partidas.licitacion'].search([("obra.id", "=", b_obra.id)])
            b_partlic = part_licitacion.browse(_search_partlic)

            c = odoo.env['contratista.contratista']
            _search_c = odoo.env['contratista.contratista'].search(
                [("id_sideop", "=", row['id_contratista'])])
            b_contra = c.browse(_search_c)

            datos_partida = {  # 
                'contrato_partida_licitacion': [[0, 0, {
                                        'id_contrato_sideop': row['num_contrato']
                                        , 'id_contratista': b_contra.id
                                        # , 'id_partida': row['id_partida'],
                                        , 'obra': b_obra.id
                                        ,'recursos': b_partlic.recursos.id
                                        , 'programaInversion': b_partlic.programaInversion.id,
                                        'numero_contrato': b_contrato.id,
                                        'monto_partida': row['importe'],
                                        'iva_partida': row['iva_total'],
                                        'total_partida': row['total'],
                                        'id_contrato_relacion': str(b_contrato.obra.id),
                                        'p_id': int(b_contrato.id),
                                        'nombre_partida': row['num_contrato'],
                                        'nombre_contrato': row['numero_contrato'],

                                         }]]
            }

            partida_al_contrato = b_contrato.write(datos_partida)

    '''if row['tipo_procedimiento'] == "AD":

        if int(_search_contrato) == 0:

            adj = odoo.env['proceso.adjudicacion_directa']
            _search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search([("numerocontrato", "=", row['numero_contrato'])])
            b_adj = adj.browse(_search_adjudicacion)

            c = odoo.env['contratista.contratista']
            _search_c = odoo.env['contratista.contratista'].search(
                [("id_sideop", "=", row['id_contratista'])])
            b_contra = c.browse(_search_c)

            unidad = odoo.env['proceso.unidad_responsable']
            _search_unidad = odoo.env['proceso.unidad_responsable'].search(
                [("id_sideop", "=", row['unidad_responsable'])])
            b_unidad = unidad.browse(_search_unidad)

            if len(str(row['fecha_inicio'])) < 10:
                fecha_inicio = None
            else:
                fecha_inicio_ = str(row['fecha_inicio'])
                fecha_inicio = fecha_inicio_[6] + fecha_inicio_[7] + fecha_inicio_[8] + \
                               fecha_inicio_[9] + fecha_inicio_[
                                   5] + fecha_inicio_[3] + fecha_inicio_[4] + fecha_inicio_[2] + \
                               fecha_inicio_[0] + fecha_inicio_[1]

            if len(str(row['fecha_termino'])) < 10:
                fecha_termino = None
            else:
                fecha_termino_ = str(row['fecha_termino'])
                fecha_termino = fecha_termino_[6] + fecha_termino_[7] + fecha_termino_[8] + \
                                fecha_termino_[9] + fecha_termino_[
                                    5] + fecha_termino_[3] + fecha_termino_[4] + fecha_termino_[2] + \
                                fecha_termino_[0] + fecha_termino_[1]

            if len(str(row['fecha'])) < 10:
                fecha = None
            else:
                fecha_ = str(row['fecha'])
                fecha = fecha_[6] + fecha_[7] + fecha_[8] + \
                        fecha_[9] + fecha_[5] + fecha_[3] + fecha_[4] + fecha_[2] + \
                        fecha_[0] + fecha_[1]

            # BUSCAR ID PARA SUPERVISION EXTERNA SI APLICA
            s_externa = odoo.env['proceso.unidad_responsable']
            _search_externa = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['num_contrato'])])
            b_externa = s_externa.browse(_search_externa)

            datos_contrato = {
                'tipo_contrato': "2",
                'adjudicacion': b_adj.id,
                'contrato': row['numero_contrato'],

                'contratista': b_contra.id,
                'name': row['objecto'],
                'descripciontrabajos': row['trabajos'],
                'unidadresponsableejecucion': b_unidad.id,

                'periodicidadretencion': row['periodo_retencion'],
                'retencion': float(row['porcentaje_retencion']),
                # 'id_sideop_partida': row['id_partida'],
                'fechainicio': fecha_inicio,
                'fechatermino': fecha_termino,
                'fecha': fecha,
                'supervisionexterna': row['supervision_externa'],
                'supervisionexterna1': b_externa.id
            }

            contrato = odoo.env['proceso.elaboracion_contrato']
            id_contrato = contrato.create(datos_contrato)

            print('SE CREO EL CONTRATO ADJUDICACION')

            contrato_id = contrato.browse(id_contrato)

            obraprogramada = odoo.env['registro.programarobra']
            _search_obra = odoo.env['registro.programarobra'].search([("Id_obraprogramada", "=", row['id_partida'])])
            b_obra = obraprogramada.browse(_search_obra)

            part_adj = odoo.env['partidas.adjudicacion']
            _search_partadj = odoo.env['partidas.adjudicacion'].search([("obra.id", "=", b_obra.id)])
            b_partadjx = part_adj.browse(_search_partadj)

            # Crear partida de esta misma linea
            datos_partida = {  # 'obra': str(partidas.obra.id),
                'contrato_partida_adjudicacion': [[0, 0, {

                                        'id_contrato_sideop': row['num_contrato']
                                        , 'id_contratista': b_contra.id
                                        # , 'id_partida': row['id_partida'],
                                        , 'obra': b_obra.id
                                        ,'recursos': b_partadjx.recursos.id
                                        , 'programaInversion': b_partadjx.programaInversion.id,
                                        'numero_contrato': contrato_id.id,
                                        'monto_partida': row['importe'],
                                        'iva_partida': row['iva_total'],
                                        'total_partida': row['total'],
                                        'id_contrato_relacion': str(contrato_id.adjudicacion.id),
                                        'p_id': int(contrato_id.id),
                                        'nombre_partida': row['num_contrato'],
                                        'nombre_contrato': row['numero_contrato'],
                                                    }]]
            }
            print('exito')
            partida_al_contrato = contrato_id.write(datos_partida)
        else:
            contra = odoo.env['proceso.elaboracion_contrato']

            _search_contratox = odoo.env['proceso.elaboracion_contrato'].search(
                [("contrato", "=", row['numero_contrato'])])
            b_contrato = contra.browse(_search_contratox)

            obraprogramada = odoo.env['registro.programarobra']
            _search_obra = odoo.env['registro.programarobra'].search([("Id_obraprogramada", "=", row['id_partida'])])
            b_obra = obraprogramada.browse(_search_obra)
            
            part_adj = odoo.env['partidas.adjudicacion']
            _search_partadj = odoo.env['partidas.adjudicacion'].search([("obra.id", "=", b_obra.id)])
            b_partadjx = part_adj.browse(_search_partadj)

            c = odoo.env['contratista.contratista']
            _search_c = odoo.env['contratista.contratista'].search(
                [("id_sideop", "=", row['id_contratista'])])
            b_contra = c.browse(_search_c)

            datos_partida = {  # 'obra': str(partidas.obra.id),
                'contrato_partida_adjudicacion': [[0, 0, {
                    
                    'id_contrato_sideop': row['num_contrato']
                    , 'id_contratista': b_contra.id
                    # , 'id_partida': row['id_partida'],
                    , 'obra': b_obra.id
                    ,'recursos': b_partadjx.recursos.id
                    , 'programaInversion': b_partadjx.programaInversion.id,
                    'numero_contrato': b_contrato.id,
                    'monto_partida': row['importe'],
                    'iva_partida': row['iva_total'],
                    'total_partida': row['total'],
                    'id_contrato_relacion': str(b_contrato.adjudicacion.id),
                    'p_id': int(b_contrato.id),
                    'nombre_partida': row['num_contrato'],
                    'nombre_contrato': row['numero_contrato'],

                                                          }]]
            }
            partida_al_contrato = b_contrato.write(datos_partida)
            print('SE REPITIO CONTRATO')'''