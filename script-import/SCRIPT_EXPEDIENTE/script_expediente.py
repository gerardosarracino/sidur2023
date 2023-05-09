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

query = ("SELECT * FROM `catalogo_documentos` INNER JOIN expediente ON catalogo_documentos.id_documento = expediente.id_expediente INNER JOIN contratos ON expediente.id_partida = contratos.id_partida where expediente.id > 17925 order by expediente.id" )
# where catalogoconceptos.id > "+str(ultimo_row_OK)+"

cursor.execute(query)

for row in cursor:

    '''categorias = odoo.env['control_expediente.control_expediente']

    datos_exp = {
            'id_sideop': row['id_documento'],
            'nombre': row['nombre_documento'],
            'etapa': str(row['etapa']),
            'orden': row['orden'],
    }

    expediente = categorias.create(datos_exp)
    print(row['nombre_documento'])'''
    _search_part = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    _search_programa2 = odoo.env['partidas.partidas'].search_count(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    if _search_programa2 == 0:
        print('NO EXISTE ESE CONTRATO', row['num_contrato'])

    else:
        print('SI EXISTE ESE CONTRATO', row['num_contrato'], row['id'])

        exp = odoo.env['partidas.partidas']

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
            'p_id': _search_part[0],
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
        expe = exp.browse(_search_part[0])
        expediente = expe.write(datos_exp)
        print('exito')
