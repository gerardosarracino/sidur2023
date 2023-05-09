import odoorpc, csv
import datetime
import mysql.connector
import time


usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('35.223.0.35', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                            host='35.223.0.35',
                            database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `estimaciones_detalles` INNER JOIN catalogoconceptos ON estimaciones_detalles.id_concepto = catalogoconceptos.id where estimaciones_detalles.id_concepto > 102537 order by catalogoconceptos.id asc" )
# where catalogoconceptos.id > "+str(ultimo_row_OK)+"

cursor.execute(query)

for row in cursor:

    _search_part = odoo.env['partidas.partidas'].search(
        [("id_partida", "=", row['id_partida'])])

    _search_programa2 = odoo.env['partidas.partidas'].search_count(
        [("id_partida", "=", row['id_partida'])])

    if _search_programa2 == 0:
        print('NO EXISTE ESE CONTRATO', row['referencia_proceso'])

    else:
        print('SI EXISTE ESE CONTRATO', row['referencia_proceso'])

        _search_partidaid = odoo.env['partidas.partidas'].search(
            [("id_partida", "=", row['id_partida'])])

        print(_search_partidaid[0])

        exp = odoo.env['partidas.partidas']

        '''if str(row['fecha']) == '':
            new_fecha = None
        else:
            new_fecha_ = str(row['fecha'])
            new_fecha = new_fecha_[6] + new_fecha_[7] + new_fecha_[8] + new_fecha_[9] + \
                            new_fecha_[5] + new_fecha_[3] + new_fecha_[4] + new_fecha_[2] + \
                            new_fecha_[0] + new_fecha_[1]'''

        if int(row['etapa']) == 0:
            etapa = []
        else:
            etapa = str(row['etapa'])

        if int(row['id_documento']) == 0:
            id_d = []
        else:
            _search_exp = odoo.env['control_expediente.control_expediente'].search(
                [("id_sideop", "=", row['id_documento'])])

            _browse_exp = odoo.env['control_expediente.control_expediente'].browse(_search_exp[0])

            id_d = _browse_exp.id

        datos_exp = {
            'tabla_control': [[0, 0, {
            'p_id': _search_partidaid[0],
            'id_sideop': row['id'],
            'id_expediente': row['id_expediente'],
            'comentarios': row['comentarios'],
            'referencia': row['referencia'],
            'aplica': row['aplica'],
            'existe': row['existe'],
            'etapa': etapa,
            'nombre': id_d,
            }]]
        }
        expe = exp.browse(_search_partidaid[0])
        expediente = expe.write(datos_exp)
