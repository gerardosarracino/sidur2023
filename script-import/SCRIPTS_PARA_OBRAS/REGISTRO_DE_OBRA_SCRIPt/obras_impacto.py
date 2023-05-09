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

query = ("SELECT * from obras_planeadas_impacto order by obras_planeadas_impacto.id desc")

cursor.execute(query)

for row in cursor:
    obra = odoo.env['registro.obra']

    _search_obra = odoo.env['registro.obra'].search(
        [("id_sideop", "=", row['id_obra'])])

    b_obra = obra.browse(_search_obra)

    print(row["id_obra"], '------',b_obra.id_sideop)

    if row["id_obra"] == b_obra.id_sideop:
        print('ya existe')

        datos_obra = {
            'beneficiados': row['beneficiados'],
            'metaFisicaProyecto': row['metaFisica'],
            'metaProyectoUnidad': row['metaUnidad'],
            'metaEjercicio': row['metaEje'],
            'metaEjercicioUnidad': row['metaEjeUnidad'],
            'justificacionTecnica': row['justificacionTecnica'],
            'justificacionSocial': row['justificacionSocial'],
        }

        obra_modificar = obra.browse(_search_obra)

        obra_modi = obra_modificar.write(datos_obra)


    else:
        print('NO EXISTE')

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