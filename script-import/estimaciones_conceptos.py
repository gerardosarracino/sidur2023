import odoorpc, csv
import datetime
import mysql.connector

import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('34.70.236.42', port=8069)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                            host='34.70.236.42',
                            database='sidur') 
cursor = cnx.cursor(dictionary=True) 

query = ("SELECT * FROM `catalogoconceptos` INNER JOIN estimaciones_detalles ON catalogoconceptos.id = estimaciones_detalles.id_concepto order by estimaciones_detalles.id asc;" )
# where catalogoconceptos.id > "+str(ultimo_row_OK)+"       where estimaciones_detalles.id > 118217 

cursor.execute(query)

for row in cursor:
    contrato = odoo.env['partidas.partidas']

    print(row['num_contrato'], ' y la id es x', row['id'])

    '''_search_contrato = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])
    b_contrato = contrato.browse(_search_contrato)

    print(b_contrato.numero_contrato.tipo_contrato)

    if str(b_contrato.numero_contrato.tipo_contrato) == '1':
        print('es licitacion -----------------')'''

    _search_estimacion = odoo.env['control.estimaciones'].search_count(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    if _search_estimacion == 0:
        print('NO EXISTE ESTA ESTIMACION')
        print(row['num_contrato'])
    else:
        print('EXISTE ESTIMACION')

        _search_estimacion2 = odoo.env['control.estimaciones'].search([("id_contrato_sideop", "=", row['num_contrato']), ("idobra", "=", row['num_estimacion']) ])

        if str(_search_estimacion2) == '[]':
            pass
        else:

            _search_estimacion3 = odoo.env['control.estimaciones'].browse(_search_estimacion2[0])

            print(row['num_estimacion'], "------" , _search_estimacion3.idobra)

            _search_partida = odoo.env['partidas.partidas'].search([("id_contrato_sideop", "=", row['num_contrato'])])
            estimaciones = odoo.env['control.estimaciones']

            _search_categoria = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                    limit=1)
            
            categorias = odoo.env['catalogo.categoria']

            if str(_search_categoria) is not '[]':
                print(_search_categoria)
                categoria = _search_categoria
                _search_cat = odoo.env['catalogo.categoria'].search(
                    [("id_sideop", "=", row['idpadre'])])
                categoria = categorias.browse(_search_cat)
                categoria = categoria.id
            else:
                print('es nons')
                categoria = None

            categoriasx = odoo.env['catalogo.categoria']

            _search_parent_id = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                    )
            b_parent = categoriasx.browse(_search_parent_id)

            datos_conceptos = {
                'conceptos_partidas': [[0, 0, {
                    'num_est': row['num_estimacion'],
                    'id_sideop': row['id_concepto'],
                    'id_partida': _search_partida[0],
                    'related_categoria_padre': b_parent.id,
                    'categoria': categoria,
                    'clave_linea': str(row['clave']),
                    'concepto': str(row['descripcion']),
                    'medida': str(row['unidad']),
                    'precio_unitario': str(row['punitario']),
                    'cantidad': str(row['cantidad']),

                    'estimacion': str(row['cantidad_ejecutada_current']),
                }]]}

            partida_seleccionada = estimaciones.browse(_search_estimacion2[0])
            
            partida_nueva = partida_seleccionada.write(datos_conceptos)
            print(' al putazo')
    
   
