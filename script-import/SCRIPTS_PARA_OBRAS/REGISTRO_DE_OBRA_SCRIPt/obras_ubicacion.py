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

query = ("SELECT * FROM `obras_planeadas_ubicacion` INNER JOIN municipios ON obras_planeadas_ubicacion.municipio = municipios.id order by obras_planeadas_ubicacion.id desc")

cursor.execute(query)

for row in cursor:
    obra = odoo.env['registro.obra']
    muni = odoo.env['generales.municipios']

    _search_obra = odoo.env['registro.obra'].search(
        [("id_sideop", "=", row['id_obra'])])

    _search_estado = odoo.env['generales.estado'].search(
        [("id_sideop", "=", row['estato'])])

    b_obra = obra.browse(_search_obra)

    _search_m = odoo.env['generales.municipios'].search(
        [("clave_municipio", "=", row['clave_municipio'])])

    b_m = muni.browse(_search_m)

    print(row["id_obra"], '------',b_obra.id_sideop)

    if row["id_obra"] == b_obra.id_sideop:
        print('ya existe')

        datos_obra = {
            'estado': _search_estado[0],
            'ubicacion': row['ubicacion'],
            'localidad': row['localidad'],
            'municipio': b_m.id,
            'partner_latitude': row['latitud'],
            'partner_longitude': row['longitud'],
            'cabeceraMunicipal': row['cabezera'],
        }

        obra_modificar = obra.browse(_search_obra)

        obra_modi = obra_modificar.write(datos_obra)


    else:
        print('NO EXISTE CREAR')

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