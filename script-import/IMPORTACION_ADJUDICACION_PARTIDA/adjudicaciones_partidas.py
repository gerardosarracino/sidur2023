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

query = ("SELECT * FROM `adjudicacion_directa_partidas`")

cursor.execute(query)

for row in cursor:
    print(row['id'])
    Id_obraprogramada = row['id_partida']
    id_sideop_adjudicacion = row['id_adjudicacion']

    search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search([('id_sideop_adjudicacion','=',id_sideop_adjudicacion)],limit=1)

    search_obra_programada = odoo.env['registro.programarobra'].search([('Id_obraprogramada','=',Id_obraprogramada)],limit=1)

    # recurso
    anexo = odoo.env['autorizacion_obra.anexo_tecnico']
    _search_anexo = odoo.env['autorizacion_obra.anexo_tecnico'].search(
        [("concepto.Id_obraprogramada", "=", row['id_partida'])])
    b_anexo = anexo.browse(_search_anexo)

    adjudicacion = odoo.env['proceso.adjudicacion_directa']

    _search_adj = odoo.env['proceso.adjudicacion_directa'].search(
        [("id_sideop_adjudicacion", "=", row['id_adjudicacion'])])

    b_adj = adjudicacion.browse(_search_adj)

    try:
        id_obra_programada = search_obra_programada[0]
#          print("Si encontro la obra programada")
    except:
        id_obra_programada = ""
        print("No encontro la obra programada en base de datos")

    try:
        id_adjudicacion = search_adjudicacion[0]
        id_adjudicacion_update = odoo.env['proceso.adjudicacion_directa'].browse(id_adjudicacion)
#           print("Si encontro la adjudicacion")
    except:
        print("No pudo encontrar la adjudicacion en la base de datos id: " + str(row['id']) + " id_partida: " + str(row['id_partida']) + " id_adjudicacion "+str(row['id_partida']))

    if id_adjudicacion_update != False:
        try:
            id_adjudicacion_update.write({
                'programar_obra_adjudicacion': [[0, 0,
                {
                    'recursos': b_anexo.id,
                    'obra': b_anexo.concepto.id,
                    'programaInversion': b_adj.programas_inversion_adjudicacion.id,
                    'id_adjudicacion': b_adj.id,
                    'id_sideop_adjudicacion': row['id'],
                    'monto_partida': row['importe'],
                    'iva_partida': row['importe_iva'],
                    'total_partida': row['total']
                }]]
            })
            print('exito')
            print(b_adj.numerocontrato)

           # print(id_adjudicacion_update)
        except:
            print("No funciono la asociacion ")