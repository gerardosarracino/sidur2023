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

query = ("SELECT * from oficios_autorizacion order by id desc")

cursor.execute(query)

for row in cursor:
    oficio = odoo.env['autorizacion_obra.oficios_de_autorizacion']

    _search_oficio = odoo.env['autorizacion_obra.oficios_de_autorizacion'].search(
        [("id_sideop", "=", row['id'])])

    b_oficio = oficio.browse(_search_oficio)

    print(row["id"])

    if row["id"] == b_oficio.id_sideop:
        print('YA EXISTE')

    else:
        print('NO EXISTE CREAR')
        if len(str(row['fecha'])) < 10:
            fecha_inicial = None
        else:
            fecha_inicial_ = str(row['fecha'])
            fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + fecha_inicial_[
                5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + fecha_inicial_[0] + fecha_inicial_[1]

        if len(str(row['fecha_recibido'])) < 10:
            fecha_recibido = None
        else:
            fecha_recibido_ = str(row['fecha_recibido'])
            fecha_recibido = fecha_recibido_[6] + fecha_recibido_[7] + fecha_recibido_[8] + fecha_recibido_[9] + fecha_recibido_[
                5] + fecha_recibido_[3] + fecha_recibido_[4] + fecha_recibido_[2] + fecha_recibido_[0] + fecha_recibido_[1]

        if str(row['fecha_vencimiento']) == "":
            fecha_venci = None
        elif len(str(row['fecha_vencimiento'])) < 10:
            fecha_venci = None
        else:
            fecha_venci_ = str(row['fecha_vencimiento'])
            fecha_venci = fecha_venci_[6] + fecha_venci_[7] + fecha_venci_[8] + fecha_venci_[9] + fecha_venci_[
                5] + fecha_venci_[3] + fecha_venci_[4] + fecha_venci_[2] + fecha_venci_[0] + fecha_venci_[1]

        datos_ofi = {
            'id_sideop': row['id'],
            'name': row['num_ofi_aut'],
            'fecha_actual': fecha_inicial,
            'fecha_de_recibido': fecha_recibido,
            'fecha_de_vencimiento': fecha_venci,
            'importe': str(row['monto']),

        }
        modal = oficio.create(datos_ofi)

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