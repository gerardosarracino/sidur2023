import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('35.238.206.12', port=8069)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='FENShFfnw7yuzF',
                              host='35.227.173.205',
                              database='sideop_febrero')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `licitaciones_apertura` where id > 2552")

cursor.execute(query)

for row in cursor:
    print(row['id'], row['id_licitacion'])

    # BUSCAR SI EXISTE LICITACION
    _search_lici = odoo.env['proceso.licitacion'].search(
        [("numerolicitacion", "=", row['id_licitacion'])])

    # BUSCAR SI EXISTE EL EVENTO SINO PARA CREARLO
    evento = odoo.env['proceso.eventos_licitacion']
    # fallo = odoo.env['proceso.contra_fallo']

    _search_evento = odoo.env['proceso.eventos_licitacion'].search(
        [("numerolicitacion_evento", "=", _search_lici)])

    b_evento = evento.browse(_search_evento)

    # contratista
    c = odoo.env['contratista.contratista']
    _search_c = odoo.env['contratista.contratista'].search(
        [("id_sideop", "=", row['id_licitante'])])
    b_contra = c.browse(_search_c)

    if str(row['posicion']) == '1':
        pos = str(row['posicion'])
    else:
        pos = None

    if str(_search_evento) == '[]':
        print('NO EXISTE EVENTO HAY QUE CREARLO')

        datos_eve = {
            'numerolicitacion_evento': _search_lici[0],
        }

        eventocreado = evento.create(datos_eve)

        contrato_id = evento.browse(eventocreado)

        datos_propuesta = {  # 'obra': str(partidas.obra.id),
            'contratista_propuesta': [[0, 0,{
                'id_sideop': row['id']
                , 'name': b_contra.id
                , 'numerolicitacion': _search_lici[0]
                , 'asiste': row['asistio']
                , 'completa': row['completa']
                , 'revision': row['revision']
                , 'paso': row['paso']
                , 'posicion': pos

                , 'monto': row['monto']
                , 'observaciones': row['observ']
            }]]
        }
        propuestax = contrato_id.write(datos_propuesta)

    # CREAR DATOS DE LA TABLA
    else:
        print('ya existe evento crear datos tabla')

        _search_lici = odoo.env['proceso.licitacion'].search(
            [("numerolicitacion", "=", row['id_licitacion'])])

        _search_evento = odoo.env['proceso.eventos_licitacion'].search(
            [("numerolicitacion_evento", "=", _search_lici)])

        b_evento = evento.browse(_search_evento)

        datos_propuesta = {  # 'obra': str(partidas.obra.id),
            'contratista_propuesta': [[0, 0, {
                'id_sideop': row['id']
                , 'name': b_contra.id
                , 'numerolicitacion': _search_lici[0]
                , 'asiste': row['asistio']
                , 'completa': row['completa']
                , 'revision': row['revision']
                , 'paso': row['paso']
                , 'posicion': pos

                , 'monto': row['monto']
                , 'observaciones': row['observ']
            }]]
        }

        propuestax = b_evento.write(datos_propuesta)

    '''Id_obraprogramada = row['id_partida']

    id_sideop_licitacion = row['num_licitacion']

    search_licitacion = odoo.env['proceso.licitacion'].search([('numerolicitacion','=', id_sideop_licitacion)], limit=1)

    print(search_licitacion)

    search_obra_programada = odoo.env['registro.programarobra'].search([('Id_obraprogramada','=', Id_obraprogramada)], limit=1)

    # recurso
    anexo = odoo.env['azutorizacion_obra.anexo_tecnico']

    _search_lici = odoo.env['proceso.licitacion'].search(
        [("numerolicitacion", "=", row['num_licitacion'])])

    b_lici = licitacion.browse(_search_lici)

    try:
        id_obra_programada = search_obra_programada[0]
#          print("Si encontro la obra programada")
    except:
        id_obra_programada = ""
        print("No encontro la obra programada en base de datos")

    print(search_licitacion)

    try:
        id_licitacion = search_licitacion
        id_licitacion_update = odoo.env['proceso.licitacion'].browse(search_licitacion)
#           print("Si encontro la adjudicacion")

    except:
        print("No pudo encontrar la adjudicacion en la base de datos id: " + str(row['id']) + " id_partida: " + str(row['id_partida']))

'''
    # if id_licitacion_update != False:
    #     id_licitacion_update.write({
    #         'programar_obra_licitacion': [[0, 0,
    #         {
    #             'recursos': b_anexo.id,
    #             'obra': b_anexo.concepto.id,
    #             'programaInversion': b_lici.programa_inversion_licitacion.id,
    #             # 'id_adjudicacion': b_lici.id,
    #             'id_sideop_partida': row['id'],
    #             'monto_partida': row['monto'],
    #         }]]
    #     })
    #     print('exito')
    #     print(b_lici.numerolicitacion)