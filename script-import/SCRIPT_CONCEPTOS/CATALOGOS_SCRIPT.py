import odoorpc, csv
import datetime
import mysql.connector
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='sidur.galartec.com',
                              database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `catalogoconceptos` where numeroContrato = 'SIDUR-PF-20-007.1880'" ) # where catalogoconceptos.id > 151819 

cursor.execute(query)

for row in cursor:
    # buscar el id de la partidajgss

    _search_partida = odoo.env['partidas.partidas'].search([("id_contrato_sideop", "=", row['numeroContrato'])])

    print(row['id'], '--- ID', row['numeroContrato'])

    partidax = odoo.env['partidas.partidas']
    b_partx = partidax.browse(_search_partida)

    # partida_ = _search_partida[0]
    idpadre = row['idpadre']

    if _search_partida:
        print('awibilt')

        if str(row['tipo']) == "1":
            print('TIPO 1')
            # tipo = "categoria"

            partida = odoo.env['partidas.partidas']
            _search_part = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['numeroContrato'])])
            b_part = partida.browse(_search_part)

            categorias = odoo.env['catalogo.categoria']

            datos = {
                'name': row['clave'],
                'descripcion': row['descripcion'],
                'id_sideop': row['id'],
                'id_partida': b_part.id
            }

            id_categoria = categorias.create(datos)

            _search_cat = odoo.env['catalogo.categoria'].search(
                [("id_sideop", "=", row['id'])])
            b_cat = categorias.browse(_search_cat)

            partidas_data = {'conceptos_partidas': [[0, 0, {
                'id_sideop': row['id'],
                'categoria': b_cat.id,
                'id_partida': b_part.id,
                'clave_linea': row['clave'],
                'concepto': row['descripcion'],
            }]]}

            partida_seleccionada = partida.browse(_search_part)

            partida_nueva = partida_seleccionada.write(partidas_data)

        elif str(row['tipo']) == "2":
            print('TIPO 2')
            # tipo = "subcategoria"

            categorias = odoo.env['catalogo.categoria']

            partida = odoo.env['partidas.partidas']
            _search_part = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['numeroContrato'])])

            b_part = partida.browse(_search_part)

            _search_parent_id = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                        )
            _search_cat = odoo.env['catalogo.categoria'].search(
                [("id_sideop", "=", row['id'])])

            b_cat = categorias.browse(_search_cat)

            b_parent = categorias.browse(_search_parent_id)

            datos = {
                'name': str(row['descripcion']),
                'descripcion': str(row['descripcion']),
                'id_sideop': str(row['id']),
                'parent_id': b_parent.id,
                'id_partida': b_part.id
            }
            id_categoria = categorias.create(datos)

            partidas_data = {'conceptos_partidas': [[0, 0, {
                'id_sideop': row['id'],
                'categoria': b_cat.id,
                'id_partida': b_part.id,
                'clave_linea': row['clave'],
                'concepto': row['descripcion'],

            }]]}

            partida_seleccionada = partida.browse(_search_partida)

            partida_nueva = partida_seleccionada.write(partidas_data)

            print('TERMINO TIPO 2')
        elif str(row['tipo']) == "3":
            print('TIPO 3')
            categoria = ""
            # tipo = "concepto"
            categorias = odoo.env['catalogo.categoria']

            _search_categoria = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                        limit=1)
            if len(_search_categoria) > 0:
                categoria = _search_categoria[0]
                _search_cat = odoo.env['catalogo.categoria'].search(
                    [("id_sideop", "=", row['id'])])
                b_cat = categorias.browse(_search_cat)
                b_catx = b_cat.id
            else:
                b_catx = None

            # b_cat2 = categorias.browse(_search_categoria)

            partida = odoo.env['partidas.partidas']
            _search_part = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['numeroContrato'])])
            b_part = partida.browse(_search_part)

            # print(b_cat2.id)

            _search_parent_id = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                        )
            b_parent = categorias.browse(_search_parent_id)

            partidas_data = {
                'conceptos_partidas': [[0, 0, {
                    'id_sideop': row['id'],
                    'categoria': b_catx,
                    'id_partida': b_part.id,
                    'clave_linea': row['clave'],
                    'concepto': row['descripcion'],
                    'medida': row['unidad'],
                    'cantidad': float(row['cantidad']),
                    'precio_unitario': float(row['punitario']),

                    'related_categoria_padre': b_parent.id
                }]]}
            partida_seleccionada = partida.browse(_search_part)

            partida_nueva = partida_seleccionada.write(partidas_data)

            print('TERMINO TIPO 3')

        elif row['idpadre'] == 0:
            print("id padre en 0")
            print("ok ", row['id'])
            idpadre = ""
            categoria = ""
            print("ok ", row['idpadre'])
        
    else:
        print('no')
