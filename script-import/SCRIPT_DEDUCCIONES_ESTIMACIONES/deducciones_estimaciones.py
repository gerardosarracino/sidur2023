import odoorpc, csv
import datetime
import mysql.connector

import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='Navojoa2020',
                            host='sidur.galartec.com',
                            database='sideop') 
cursor = cnx.cursor(dictionary=True) 

query = ("SELECT * FROM `deducciones` INNER JOIN estimaciones_deduciones ON deducciones.id = estimaciones_deduciones.id_deducion WHERE estimaciones_deduciones.num_contrato = 'SIDUR-ED-19-196.1846' and estimaciones_deduciones.num_estimacion = '2' order by estimaciones_deduciones.id asc;" ) #  WHERE id > 15965 where estimaciones_deduciones.id > 20382

cursor.execute(query)

for row in cursor:

    _search_esti_count = odoo.env['control.estimaciones'].search_count(
            [("num_contrato", "=", row['num_contrato']), ("idobra","=",row['num_estimacion']),  ("tipo_estimacion","=", row['tipoEstimacion'])])

    print(row['num_contrato'], 'su id es ', row['id'])

    if _search_esti_count == 0:
        print('no existe')

    else:
        print('existe', row['num_contrato'])

        esti = odoo.env['control.estimaciones']

        _search_esti = odoo.env['control.estimaciones'].search(
            [("num_contrato", "=", row['num_contrato']), ("idobra","=",row['num_estimacion']),  ("tipo_estimacion","=", row['tipoEstimacion'])]) # , ("tipo_estimacion","=",row['tipoEstimacion'])

        # dedu = odoo.env['control.deducciones'].search([("id_sideop", "=", row['id'])])

        b_est = odoo.env['control.estimaciones'].browse(_search_esti)

        '''print(row['num_estimacion'], '---NUM DE ESTI--- ', b_est.idobra)

        print(row['tipoEstimacion'], '---TIPO DE ESTIMACION---- ', b_est.tipo_estimacion)'''

        if str(row['num_estimacion']) == str(b_est.idobra):

            # print(' NUMERO DE LA ESTIMACION')
            # print(b_est.idobra, '-------', row['num_estimacion'])

            datos_deducciones = {
                'deducciones': [[0, 0, {
                    'name': row['nombre_deduccion'],
                    'porcentaje': float(row['porcentaje']),
                    'id_sideop': row['id'],
                    'num_esti': row['num_estimacion'],
                    'valor': float(row['importe_deducion']),
                    'estimacion': b_est.id,
                }]]}

            deduc = esti.browse(b_est.id)

            nueva_deduccion = deduc.write(datos_deducciones)
            print('EXITOO!!!!!!!-----------')
        else:
            

            print(row['num_contrato'])
            print(b_est.idobra, '-------', row['num_estimacion'])

            print('otro num estimacion ----------------------')

        
