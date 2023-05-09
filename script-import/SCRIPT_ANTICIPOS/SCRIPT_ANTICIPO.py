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

query = ("SELECT * FROM `contratos_anticipo` order by contratos_anticipo.id asc;")

cursor.execute(query)

for row in cursor:
    print(row['id'], ' esta es la id -------', 'y el contrato es x ', row['num_contrato'])

    _search_part = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    _search_programa2 = odoo.env['partidas.partidas'].search_count(
        [("id_contrato_sideop", "=", row['num_contrato'])])
    
    if _search_programa2 == 0:
        print('NO EXISTE ESE CONTRATO --------------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', row['num_contrato'])

    else:
        print('SI EXISTE ESE CONTRATO', row['num_contrato'])

        partida = odoo.env['partidas.partidas']

        b_contrato = partida.browse(_search_part)
        
        if len(str(row['fecha_fianza'])) < 10:
            new_fecha = None
        else:
            new_fecha_ = str(row['fecha_fianza'])
            new_fecha = new_fecha_[6] + new_fecha_[7] + new_fecha_[8] + new_fecha_[9] + \
                        new_fecha_[5] + new_fecha_[3] + new_fecha_[4] + new_fecha_[2] + \
                        new_fecha_[0] + new_fecha_[1]

        if len(str(row['fecha'])) < 10:
            new_fecha2 = None
        else:
            new_fecha2_ = str(row['fecha'])
            new_fecha2 = new_fecha2_[6] + new_fecha2_[7] + new_fecha2_[8] + new_fecha2_[9] + \
                        new_fecha2_[5] + new_fecha2_[3] + new_fecha2_[4] + new_fecha2_[2] + \
                        new_fecha2_[0] + new_fecha2_[1]

        xd = '0.' + str(row['anticipo_material'])
        xd2 = '0.' + str(row['anticipo_inicio'])
        xd3 = '0.' + str(row['total_anticipo_por'])

        datos_anticipo = {
            'fecha_fianza': new_fecha,
            'fecha_anticipos': new_fecha2,
            'porcentaje_anticipo': float(xd2),
            'anticipo_material': float(xd),
            'total_anticipo_porcentaje': float(xd3),
            'anticipo_a': float(row['importe']),
            'iva_anticipo': row['iva_anticipo'],
            'total_anticipo': row['total_anticipo'],
            'numero_fianza': row['num_fianza'],
            'afianzadora': row['afianzadora'],
        }
        anticipo = b_contrato.write(datos_anticipo)
        print('exito')

