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

query = ("SELECT * from obras_planeadas order by id desc")

cursor.execute(query)

for row in cursor:
    obra = odoo.env['registro.obra']

    _search_obra = odoo.env['registro.obra'].search(
        [("id_sideop", "=", row['id'])])

    b_obra = obra.browse(_search_obra)

    _search_eje = odoo.env['registro.ejercicio'].search(
        [("name", "=", row['eje'])])

    print(row["id"])

    if row["id"] == b_obra.id_sideop:
        print('ya existe')
    else:
        print('NO EXISTE CREAR')

        #TODO ESTE DESMADRE PARA NO CAMBIAR IDS
        origen = 1
        if str(row['origen']) == '48':
            origen = 1
        elif str(row['origen']) == '49':
            origen = 2
        elif str(row['origen']) == '50':
            origen = 3
        elif str(row['origen']) == '24':
            origen = 4
        else:
            origen = 1

        tipo = 1
        if str(row['tipo']) == '46':
            tipo = 1
        elif str(row['tipo']) == '47':
            tipo = 2
        elif str(row['tipo']) == '48':
            tipo = 3
        elif str(row['tipo']) == '49':
            tipo = 4
        elif str(row['tipo']) == '50':
            tipo = 5
        elif str(row['tipo']) == '51':
            tipo = 6
        elif str(row['tipo']) == '52':
            tipo = 7
        elif str(row['tipo']) == '53':
            tipo = 8
        elif str(row['tipo']) == '54':
            tipo = 9
        elif str(row['tipo']) == '55':
            tipo = 10
        elif str(row['tipo']) == '58':
            tipo = 11
        else:
            tipo = 1

        unidad = 1
        if str(row['id_unidad']) == '5':
            unidad = 1
        elif str(row['id_unidad']) == '6':
            unidad = 2
        elif str(row['id_unidad']) == '7':
            unidad = 3
        elif str(row['id_unidad']) == '8':
            unidad = 4
        elif str(row['id_unidad']) == '9':
            unidad = 5
        else:
            unidad = 1

        tipoProyecto = 1
        if str(row['tipoProyecto']) == '1':
            tipoProyecto = 1
        elif str(row['tipoProyecto']) == '2':
            tipoProyecto = 2
        elif str(row['tipoProyecto']) == '3':
            tipoProyecto = 3
        else:
            tipoProyecto = 1

        tipoObraEtapa = 1
        if str(row['tipoObraEtapa']) == '1':
            tipoObraEtapa = 1
        elif str(row['tipoObraEtapa']) == '2':
            tipoObraEtapa = 2
        elif str(row['tipoObraEtapa']) == '3':
            tipoObraEtapa = 3
        elif str(row['tipoObraEtapa']) == '4':
            tipoObraEtapa = 4
        else:
            tipoObraEtapa = 1

        datos_obra = {
            'id_sideop': row['id'],
            'ejercicio': _search_eje[0],
            'numero_obra': row['num_obra'],
            'origen': origen,
            'monto': row['monto'],
            'descripcion': row['descripcionObra'],
            'problematica': row['observaciones'],
            'tipoObra': tipo,
            'unidadadminsol': unidad,
            'tipoproyecto': tipoProyecto,
            'tipoobraetapa': tipoObraEtapa,
            'grupoObra': row['grupoObra'],
        }
        modal = obra.create(datos_obra)

        print('exito')


cursor.close()
cnx.close()

print('simon xd')
'''with open('sideop_obras_planeadas.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        modi = odoo.env['registro.obra']

        _search_eje = odoo.env['registro.ejercicio'].search(
            [("name", "=", row['eje'])])

        if str(row['id_unidad']) == '0':
            print('SI ENTRO ALV')
            unidadadm = 1
        else:
            unidadadm = row['id_unidad']

        datos_obra = {
            'id_sideop': row['id'],
            'ejercicio': _search_eje[0],
            'numero_obra': row['num_obra'],
            'origen': row['origen'],
            'monto': row['monto'],
            'descripcion': row['descripcionObra'],
            'problematica': row['observaciones'],
            'tipoObra': row['tipo'],
            'unidadadminsol': unidadadm,
            'tipoproyecto': row['tipoProyecto'],
            'tipoobraetapa': row['tipoObraEtapa'],
            'grupoObra': row['grupoObra'],
        }
        modal = modi.create(datos_obra)

        print('exito')
        print(row['id'])'''