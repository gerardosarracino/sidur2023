import odoorpc, csv
import datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('SIDUR.OBRAS', usuario, password)

with open('sideop_unidad_administrativa.csv', encoding="latin1") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        b = odoo.env['registro.unidadadminsol']

        datos_adm = {
            'name': row['descripcion'],
        }
        modal = b.create(datos_adm)
        print('exito')