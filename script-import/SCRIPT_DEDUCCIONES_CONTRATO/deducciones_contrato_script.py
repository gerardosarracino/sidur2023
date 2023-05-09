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

query = ("SELECT * FROM `contratos_deducciones` INNER JOIN deducciones ON contratos_deducciones.id_deduccion = deducciones.id")

cursor.execute(query)

for row in cursor:
    print(row['id'])
    _search_contrato = odoo.env['proceso.elaboracion_contrato'].search_count(
        [("contrato", "=", row['num_contrato'])])

    if _search_contrato == 0:
        print('NO EXISTE ESTE CONTRATO')
        print(row['num_contrato'])
    else:
        print('EXISTE CONTRATO')
        print(row['num_contrato'])

        contratos = odoo.env['proceso.elaboracion_contrato']

        _search_contrato = odoo.env['proceso.elaboracion_contrato'].search(
            [("contrato", "=", row['num_contrato'])])

        print(row['nombre_deduccion'])

        dedu = odoo.env['generales.deducciones'].search(
            [("id_sideop", "=", row['id'])])
        print(dedu[0])

        datos_deducciones = {
            'deducciones': [[1, dedu[0], {
                'name': row['nombre_deduccion'],
                'porcentaje': row['porcentaje'],
            }]]}

        contrato = contratos.browse(_search_contrato[0])

        nueva_deduccion = contrato.update(datos_deducciones)
