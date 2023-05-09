import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='FENShFfnw7yuzF',
                              host='35.227.173.205',
                              database='sideop20')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `contratos`")

cursor.execute(query)

for row in cursor:
    if row['tipo_procedimiento'] == "AD":
        tipo_contrato = "2"  # 2 es para adjudicacion

        _search_contrato = odoo.env['proceso.elaboracion_contrato'].search_count(
            [("contrato", "=", row['num_contrato'])])

        if _search_contrato == 0:

            #crear contrato

            #tomar en cuenta el contratista_sideop
            _search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search(
                [("numerocontrato", "=", row['referencia'])], limit=1)

            try:
                adjudicacion = _search_adjudicacion[0]
            except:
                print("error al buscar contrato" + str(row['num_contrato']))

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
                                     fecha_[9] + fecha_[
                                         5] + fecha_[3] + fecha_[4] + fecha_[2] + \
                                     fecha_[0] + fecha_[1]

            datos_contrato = {
                'tipo_contrato': tipo_contrato,
                'adjudicacion': adjudicacion,
                'contrato': row['numero_contrato'],
                'num_contrato_sideop': row['num_contrato'],

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
            }

            contrato = odoo.env['proceso.elaboracion_contrato']
            id_contrato = contrato.create(datos_contrato)
            print('se creo')

            contrato_id = contrato.browse(id_contrato)

            contra = odoo.env['proceso.elaboracion_contrato']
            _search_contratox = odoo.env['proceso.elaboracion_contrato'].search(
                [("contrato", "=", row['num_contrato'])])
            b_contra = contra.browse(_search_contratox)

            part_adj = odoo.env['partidas.adjudicacion']
            _search_partadj = odoo.env['partidas.adjudicacion'].search(
                [("id_adjudicacion", "=", b_contra.id)])
            b_partadj = part_adj.browse(_search_partadj)

            #Crear partida de esta misma linea
            datos_partida = {         # 'obra': str(partidas.obra.id),
                'contrato_partida_adjudicacion': [[0, 0, {'id_contrato_sideop': row['num_contrato']
                                                             ,'id_contratista': row['id_contratista']
                                                             ,'id_partida': row['id_partida']
                                                             ,'recursos': b_partadj.recursos.id
                                                             ,'programaInversion': b_partadj.programaInversion.id,
                                                              'monto_partida': row['importe'],
                                                              'iva_partida': row['iva_total'],
                                                              'total_partida': row['total'],
                                                              # 'nombre_partida': str(id_contrato),
                                                              'id_contrato_relacion': str(adjudicacion),
                                                              'p_id': str(1),
                                                            'obra': b_partadj.obra.id,
                                                              }]]
            }
            print('exito')
            partida_al_contrato = contrato_id.write(datos_partida)
        else:
            contra = odoo.env['proceso.elaboracion_contrato']
            _search_contratox = odoo.env['proceso.elaboracion_contrato'].search_count(
                [("contrato", "=", row['num_contrato'])])
            b_contra = contra.browse(_search_contratox)

            _search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search(
                [("numerocontrato", "=", row['referencia'])], limit=1)

            contrato = odoo.env['proceso.elaboracion_contrato']
            contrato_id = contrato.browse(_search_contratox)

            part_adj = odoo.env['partidas.adjudicacion']
            _search_partadj = odoo.env['partidas.adjudicacion'].search(
                [("id_adjudicacion", "=", b_contra.id)])
            b_partadj = part_adj.browse(_search_partadj)

            try:
                adjudicacion = _search_adjudicacion[0]
            except:
                print("error al buscar contrato" + str(row['num_contrato']))

            _search_id_contrato = odoo.env['proceso.elaboracion_contrato'].search(
            [("contrato", "=", row['numero_contrato'])])
            datos_partida = {  # 'obra': str(partidas.obra.id),
                'contrato_partida_adjudicacion': [[0, 0, {'id_contrato_sideop': row['num_contrato']
                                                        , 'id_contratista': row['id_contratista']
                                                        , 'id_partida': row['id_partida']
                                                        , 'recursos': b_partadj.recursos.id
                                                        , 'programaInversion': b_partadj.programaInversion.id,
                                                          'monto_partida': row['importe'],
                                                          'iva_partida': row['iva_total'],
                                                          'total_partida': row['total'],
                                                          # 'nombre_partida': str(id_contrato),
                                                          'id_contrato_relacion': str(adjudicacion),
                                                          'p_id': str(1),
                                                          'obra': b_partadj.obra.id,
                                                          }]]
            }
            partida_al_contrato = contrato_id.write(datos_partida)
            print('SE REPITIO CONTRATO')