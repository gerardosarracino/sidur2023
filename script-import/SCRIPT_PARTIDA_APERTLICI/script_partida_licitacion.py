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

query = ("SELECT * FROM `licitaciones_apertura_partidas`")

cursor.execute(query)

for row in cursor:
    print('la id es: ', row['id'], ' con su licitacion:', row['num_licitacion'])

    Id_obraprogramada = row['id_partida']

    id_sideop_licitacion = row['num_licitacion']

    search_licitacion = odoo.env['proceso.licitacion'].search([('numerolicitacion','=', id_sideop_licitacion)], limit=1)

    search_obra_programada = odoo.env['registro.programarobra'].search([('Id_obraprogramada','=', Id_obraprogramada)], limit=1)

    # recurso
    anexo = odoo.env['autorizacion_obra.anexo_tecnico']

    _search_anexo = odoo.env['autorizacion_obra.anexo_tecnico'].search(
        [("concepto.Id_obraprogramada", "=", row['id_partida'])])
    b_anexo = anexo.browse(_search_anexo)

    licitacion = odoo.env['proceso.licitacion']

    _search_lici = odoo.env['proceso.licitacion'].search(
        [("numerolicitacion", "=", row['num_licitacion'])])

    b_lici = licitacion.browse(_search_lici)

    try:
        id_obra_programada = search_obra_programada[0]
#          print("Si encontro la obra programada")
    except:
        id_obra_programada = ""
        print("No encontro la obra programada en base de datos")


    try:
        id_licitacion = search_licitacion
        id_licitacion_update = odoo.env['proceso.licitacion'].browse(search_licitacion)
#           print("Si encontro la adjudicacion")

    except:
        print("No pudo encontrar la adjudicacion en la base de datos id: " + str(row['id']) + " id_partida: " + str(row['id_partida']))

    # APERTURA

    evento = odoo.env['proceso.eventos_licitacion']
    propuesta = odoo.env['proceso.contra_propuestas']

    _search_evento = odoo.env['proceso.eventos_licitacion'].search(
        [("numerolicitacion_evento", "=", _search_lici)])
    b_eve = evento.browse(_search_evento)

    _search_propuesta = odoo.env['proceso.contra_propuestas'].search(
        [("numerolicitacion", "=", _search_lici)])
    b_propuesta = propuesta.browse(_search_propuesta)

    c = odoo.env['contratista.contratista']
    _search_c = odoo.env['contratista.contratista'].search(
        [("id_sideop", "=", row['id_licitante'])])
    b_contra = c.browse(_search_c)

    print('este licitante deberia de ser: ', b_contra.name)

    for i in b_propuesta:
        if b_contra.id == i.name.id:
            print('es el mismo contratista', i.name.name)

            if id_licitacion_update != False:
                # propuestab = odoo.env['proceso.contra_propuestas'].browse(id_licitacion_update.id)

                b_propuestax = propuesta.browse(i.id)

                datos_p = {
                    'programar_obra_licitacion2': [[0, 0,
                    {
                        'recursos': b_anexo.id,
                        'licitacion_id': id_licitacion_update.id,
                        'obra': b_anexo.concepto.id,
                        'programaInversion': b_lici.programa_inversion_licitacion.id,
                        # 'id_adjudicacion': b_lici.id,
                        'id_sideop_partida': row['id'],
                        'monto_partida': float(row['monto']),
                    }]]
                }

                p = b_propuestax.write(datos_p)

                print('exito', b_lici.numerolicitacion)

        else:
            print('no es el mismo', i.name.name)
