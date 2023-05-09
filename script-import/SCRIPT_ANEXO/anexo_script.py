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

query = ("SELECT * FROM `partida_recursos` INNER JOIN obras_programadas ON partida_recursos.id_partida = obras_programadas.id order by partida_recursos.id desc;")

#SELECT * FROM `partida_recursos` INNER JOIN obras_programadas ON partida_recursos.id_partida = obras_programadas.id WHERE partida_recursos.id = 1529

cursor.execute(query)

for row in cursor:
    anexo = odoo.env['autorizacion_obra.anexo_tecnico']
    of = odoo.env['autorizacion_obra.oficios_de_autorizacion']
    ob = odoo.env['registro.programarobra']
    x = odoo.env['generales.programas_inversion']

    _search_anexo = odoo.env['autorizacion_obra.anexo_tecnico'].search(
        [("id_anexo_sideop", "=", row['id'])])

    _search_ofi = odoo.env['autorizacion_obra.oficios_de_autorizacion'].search(
        [("id_sideop", "=", row['id_oficio'])])

    _search_obra = odoo.env['registro.programarobra'].search(
        [("Id_obraprogramada", "=", row['id_partida'])])

    _search_x = odoo.env['generales.programas_inversion'].search(
        [("id_sideop", "=", row['id_programa'])])

    b_anexo = anexo.browse(_search_anexo)
    b_ofi = of.browse(_search_ofi)
    b_obra = ob.browse(_search_obra)
    b_x = x.browse(_search_x)

    print(row["id"])

    if row["id"] == b_anexo.id_anexo_sideop:
        print('YA EXISTE')

    else:
        print('NO EXISTE CREAR')

        print('la id es x ', row['id'], ' id de la obra x', row['id_partida'])
        
        print(b_ofi.id)

        datos_anexo = {
            'id_anexo_sideop': row['id'],
            'id_partida_sideop': row['id_partida'],
            'id_oficio_sideop': row['id_oficio'],
            'name': b_ofi.id,

            'claveobra': row['numero_obra'],
            'clave_presupuestal': str(row['clave_presupuestal']),
            'federal': str(row['federal']),
            'estatal': str(row['estatal']),
            'municipal': str(row['municipal']),
            'otros': str(row['otro']),

            'concepto': b_obra.id,
            'nombre_prog': str(b_x.name),

        }
        # modal = anexo.create(datos_anexo)

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