import odoorpc, csv
import datetime
import mysql.connector
from datetime import datetime
import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='Navojoa2020',
                            host='sidur.galartec.com',
                            database='sideop') 
cursor = cnx.cursor(dictionary=True) 

query = ("SELECT * FROM `sorutacritica` WHERE num_contrato = 'SIDUR-ED-19-031.1655'") #  WHERE id > 8277

cursor.execute(query)

for row in cursor:
    # CONTAR SI EXISTE LA PARTIDA PARA PODER PROSEGUIR

    # EN SIDEOP ESTA MAL ESCRITO, TIENE PUNTO EN VEZ DE GUION
    if str(row['num_contrato']) == 'SIDUR-ED.-18-278.1551':
        numC = 'SIDUR-ED-18-278.1551'
    else:
        numC = row['num_contrato']

    _search_part = odoo.env['partidas.partidas'].search_count(
        [("id_contrato_sideop", "=", str(numC) )])

    # BUSCAR LA PARTIDA MISMA
    _search_part2 = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", str(numC))])

    print(row['Id'], ' iddd')

    # SI EXISTE PARTIDA ENTONCES....
    if _search_part >= 1:

        print(row['num_contrato'])

        print('hay partida')
        # SI LA CONDICION DEL TIPO EN EL EXCEL ES IGUAL A UNO ENTONCES ES UN FRENTE
        if str(row['Tipo']) == '1':
            print('tipo 1')
            # BUSQUEDA EN LA CLASE DEL FRENTE MANY2ONE
            frente = odoo.env['proceso.frente']
            # VAMOS A BUSCAR EN LA PARTIDA
            partida2 = odoo.env['partidas.partidas']

            s_frente = odoo.env['proceso.frente'].search(
            [("id_sideop", "=", row['Id'])])

            frentex = frente.browse(s_frente)

            # crear FRENTE
            '''datos_frente = {'nombre': str(row['Nombre']),
                            'id_sideop': row['Id'],
                            'id_partida': _search_part2[0],
            }
            # SE CREA EL FRENTE
            hacia_frente = frente.create(datos_frente)'''

 

            # VAMOS A BUSCAR EN LA PARTIDA
            tabla = odoo.env['partidas.partidas'] # EN EL ODOO LO QUE VIENE SIENDO PROGRAMA FRENTE DE TRABAJO
            # crear datos en tabla
            partidas_ruta2 = {'ruta_critica': [[0, 0, {
                                'frente': frentex.id,
                                'id_partida': _search_part2[0],
                                # 'name': str(row['Nombre']),
                                }]]}

            #
            tabla_seleccionada = partida2.browse(_search_part2[0])

            tabla_creada = tabla_seleccionada.write(partidas_ruta2)

        # SI EL TIPO ES DOS ES ACTIVIDAD
        else:
            partida2 = odoo.env['proceso.rc']
            print('tipo 2')
            partida = odoo.env['partidas.partidas']

            print(_search_part2[0])

            if row['PorcentajeEstimado'] is None:
                # print('es null')
                por = 0
            else:
                # print('tiene wea ', row['PorcentajeEstimado'])
                por = str(row['PorcentajeEstimado'])
            
            print(por)

            datos_ruta = {
                'ruta_critica': [[0, 0, {'name': str(row['Nombre']),
                                        'id_partida': _search_part2[0],
                                        'porcentaje_est': por
                                            }]]
            }

            partida_seleccionada = partida.browse(_search_part2[0])
            hacia_rc = partida_seleccionada.write(datos_ruta)
            print('EXITO')

    # LA PARTIDA NO EXISTE
    else:
        print(row['num_contrato'])

        print('no existe este contrato')