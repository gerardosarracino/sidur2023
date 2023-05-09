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
                            database='sideop_marzo') 
cursor = cnx.cursor(dictionary=True) 


query = ("SELECT * from obras_programadas order by obras_programadas.id asc;")

cursor.execute(query)

for row in cursor:
    obra = odoo.env['registro.programarobra']

    _search_obrap = odoo.env['registro.programarobra'].search(
        [("Id_obraprogramada", "=", row['id'])])

    b_obrap = obra.browse(_search_obrap)

    if str(b_obrap.obra_planeada.ejercicio.name) == '2020':
        print('es 2020')
    else:


        p = odoo.env['generales.programas_inversion']
        m = odoo.env['generales.modalidades']

        if str(row['id']) != str(b_obrap.Id_obraprogramada):
            print('ya existe')
        else:
            print('ACTUALIZAR')
            # print('la id es x ', row['id'], ' id de la obra x', row['id_obra'], 'la descripcion es ',row['descripcionTotal'],)

            obra_planeada = odoo.env['registro.obra']

            _search_obra = odoo.env['registro.obra'].search(
                [("id_sideop", "=", row['id_obra'])])

            b_obra = obra_planeada.browse(_search_obra)

            _search_p = odoo.env['generales.programas_inversion'].search(
                [("id_sideop", "=", str(row['id_programa']))])

            _search_m = odoo.env['generales.modalidades'].search(
                [("id_sideop", "=", str(row['catProgramatica']))])

            b_p = p.browse(_search_p)
            b_m = m.browse(_search_m)

            print(row["id"])

            if row["id_obra"] == b_obra.id_sideop:

                print('seguir')
                '''if len(str(row['fechaPInicio'])) < 10:
                    fecha_presentacion = None
                else:
                    fecha_inicial_ = str(row['fechaPInicio'])
                    fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + fecha_inicial_[
                        5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + fecha_inicial_[0] + fecha_inicial_[1]

                if len(str(row['fechaPTermino'])) < 10:
                    fecha_presentacion = None
                else:
                    fecha_termino_ = str(row['fechaPTermino'])
                    fecha_termino = fecha_termino_[6] + fecha_termino_[7] + fecha_termino_[8] + fecha_termino_[9] + fecha_termino_[
                        5] + fecha_termino_[3] + fecha_termino_[4] + fecha_termino_[2] + fecha_termino_[0] + fecha_termino_[1]'''

                datos_obra = {
                    'obra_adj_lic': True
                    # 'Id_obraprogramada': row['id'],
                    # 'programaInversion': b_p.id,
                    # 'obra_planeada': b_obra.id,
                    # 'categoriaProgramatica': b_m.id,

                    # 'fechaProbInicio': str(fecha_inicial),
                    # 'fechaProbTermino': str(fecha_termino),
                    # 'descripTotalObra': str(row['descripcionTotal']),
                    # 'conceptoEjecutar': str(row['conceptosEjecutar']),
                    # 'avanceFisicoActual': row['avanzeFisco'],
                    # 'avanceProgCierreEjerci': row['avanzeProgramadoCierre'],
                    # 'modalidadEjecucion': str(row['modalidadEje']),

                }
                modal = b_obrap.write(datos_obra)

                print('exito')
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