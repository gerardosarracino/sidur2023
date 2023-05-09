import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('34.70.236.42', port=8069)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='34.70.236.42',
                              database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `partidas_licitadas` INNER JOIN adjudicacion_directa ON partidas_licitadas.numero_contrato = adjudicacion_directa.num_contrato where partidas_licitadas.numero_contrato = 'SIDUR-ED-16-081'")

cursor.execute(query)

for row in cursor:
    print('la id es x', row['id'], ' y el contrato es x', row['numero_contrato'])
    Id_obraprogramada = row['clave_partida']
    id_sideop_adjudicacion = row['numero_contrato']

    
    search_adjudicacion = odoo.env['proceso.adjudicacion_directa'].search([('numerocontrato','=',id_sideop_adjudicacion)],limit=1)
    if str(search_adjudicacion) == '[]':
        print('error en esta madre', 'referencia' , row['referencia'], 'contrato x ', row['numero_contrato'])
    else:
        search_obra_programada = odoo.env['registro.programarobra'].search([('Id_obraprogramada','=',Id_obraprogramada)],limit=1)

        # recurso
        anexo = odoo.env['autorizacion_obra.anexo_tecnico']
        _search_anexo = odoo.env['autorizacion_obra.anexo_tecnico'].search(
            [("concepto.Id_obraprogramada", "=", row['clave_partida'])])
        b_anexo = anexo.browse(_search_anexo)

        adjudicacion = odoo.env['proceso.adjudicacion_directa']

        _search_adj = odoo.env['proceso.adjudicacion_directa'].search(
            [("numerocontrato", "=", row['numero_contrato'])])

        print(_search_adj)

        b_adj = adjudicacion.browse(_search_adj)

        if b_adj.programar_obra_adjudicacion:
            print(' YA TIENE PARTIDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        else:
            print('nel')

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

                if id_adjudicacion_update != False:
                    try:
                        datos_partida = {
                            'programar_obra_adjudicacion': [[0, 0,
                                                            {
                                                                'recursos': b_anexo.id,
                                                                'obra': b_anexo.concepto.id,
                                                                'programaInversion': b_adj.programas_inversion_adjudicacion.id,
                                                                'id_adjudicacion': b_adj.id,
                                                                'id_sideop_adjudicacion': row['id'],
                                                                'monto_partida': row['importe'],
                                                                'iva_partida': row['iva'],
                                                                'total_partida': row['total']
                                                            }]]
                        }

                        partidas = id_adjudicacion_update.write(datos_partida)
                        print('exito')

                    # print(id_adjudicacion_update)
                    except:
                        print("No funciono la asociacion ")

            except:
                print("No pudo encontrar la adjudicacion en la base de datos id: ", row['id'] , " id_partida: " , row['clave_partida'], ' la adj es ', row['referencia'])

