import odoorpc, csv
import datetime

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

with open('estimaciones_deduciones.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        _search_esti_count = odoo.env['control.estimaciones'].search_count(
            [("num_contrato", "=", row['num_contrato'])])

        if _search_esti_count == 0:
            print('.')

        else:
            print('existe', row['num_contrato'])

            esti = odoo.env['control.estimaciones']

            _search_esti = odoo.env['control.estimaciones'].search(
                [("num_contrato", "=", row['num_contrato']), ("idobra","=",row['num_estimacion'])])

            # dedu = odoo.env['control.deducciones'].search([("id_sideop", "=", row['id'])])

            b_est = odoo.env['control.estimaciones'].browse(_search_esti[0])

            if row['num_estimacion'] == b_est.idobra:

                print(' NUMERO DE LA ESTIMACION')
                print(b_est.idobra, '-------', row['num_estimacion'])

                datos_deducciones = {
                    'deducciones': [[0, 0, {
                        'name': row['nombre_deduccion'],
                        'porcentaje': row['porcentaje'],
                        'id_sideop': row['id'],
                        'num_esti': row['num_estimacion'],
                        'valor': row['importe_deducion'],
                    }]]}

                deduc = esti.browse(_search_esti[0])

                nueva_deduccion = deduc.write(datos_deducciones)
                print('EXITOO!!!!!!!-----------')
            else:
                _search_estix = odoo.env['control.estimaciones'].search(
                    [("idobra", "=", row['num_estimacion'])])

                print(row['num_contrato'])
                print(b_est.idobra, '-------', row['num_estimacion'])

                print('otro num estimacion')
