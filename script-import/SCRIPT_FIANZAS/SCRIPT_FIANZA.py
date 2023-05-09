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

query = ("SELECT * FROM `contratos_afianzas` order by contratos_afianzas.id asc;")

cursor.execute(query)

for row in cursor:
    print(row['id'], ' esta es la id -------', 'y el contrato es x ', row['num_contrato'])

    _search_contrato = odoo.env['proceso.elaboracion_contrato'].search(
        [("contrato", "=", row['num_contrato'])])

    _search_contratoc = odoo.env['proceso.elaboracion_contrato'].search_count(
        [("contrato", "=", row['num_contrato'])])
    
    if _search_contratoc == 0:
        print('NO EXISTE ESE CONTRATO --------------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', row['num_contrato'])

    else:
        print('SI EXISTE ESE CONTRATO', row['num_contrato'])

        contrato = odoo.env['proceso.elaboracion_contrato']

        b_contrato = contrato.browse(_search_contrato)
        
        if len(str(row['fecha_fianza'])) < 10:
            new_fecha = None
        else:
            new_fecha_ = str(row['fecha_fianza'])
            new_fecha = new_fecha_[6] + new_fecha_[7] + new_fecha_[8] + new_fecha_[9] + \
                        new_fecha_[5] + new_fecha_[3] + new_fecha_[4] + new_fecha_[2] + \
                        new_fecha_[0] + new_fecha_[1]

        datos_fianza = {
            'fianzas': [[0, 0,{
                             'fecha_fianza_fianzas': new_fecha,
                            'tipo_fianza': str(row['tipo_fianza']),
                            'numero_fianza_fianzas': row['num_fianza'],
                            'afianzadora_fianzas': row['afianzadora'],
                            'monto': row['monto'],
                        }]]}

        anticipo = b_contrato.write(datos_fianza)
        print('exito')

