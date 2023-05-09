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

query = ("SELECT * FROM `oficios_cancelacion`")

cursor.execute(query)

for row in cursor:
    cancelar = odoo.env['autorizacion_obra.cancelarrecurso']
    of = odoo.env['autorizacion_obra.anexo_tecnico']

    _search_cancelar = odoo.env['autorizacion_obra.cancelarrecurso'].search(
        [("id_sideop", "=", row['id'])])

    _search_ofi = odoo.env['autorizacion_obra.anexo_tecnico'].search(
        [("id_anexo_sideop", "=", row['id'])])

    b_cancelar = cancelar.browse(_search_cancelar)
    b_ofi = of.browse(_search_ofi)

    print(row["id"])

    if str(row["id"]) == str(b_cancelar.id_sideop):
        print('YA EXISTE')

    else:
        print('NO EXISTE CREAR')

        if str(row['fecha']) == "":
            fecha_venci = None
        else:
            fecha_venci_ = str(row['fecha'])
            fecha_venci = fecha_venci_[6] + fecha_venci_[7] + fecha_venci_[8] + fecha_venci_[9] + fecha_venci_[
                5] + fecha_venci_[3] + fecha_venci_[4] + fecha_venci_[2] + fecha_venci_[0] + fecha_venci_[1]

        datos_cancelar = {
            'id_sideop': row['id'],
            'name': b_ofi.id,
            'nooficio': row['num_ofi_can'],
            'fecha': fecha_venci,
            'federalc': str(row['federal']),
            'estatalc': str(row['estatal']),
            'municipalc': str(row['municipal']),
            'otrosc': str(row['otros']),

        }
        modal = cancelar.create(datos_cancelar)

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