import odoorpc, csv

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

partidas = odoo.env['partidas.partidas']
with open('catalogoconceptos.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #buscar el id de la partida
        numero_contrato = str(row['numeroContrato'])

        _search_partida = odoo.env['partidas.partidas'].search([("id_contrato_sideop","=",numero_contrato)])
        
        if len(_search_partida) == 0:
            print('ES LICITACION')
        else:

            try:
                partida_ = _search_partida[0]
                idpadre = row['idpadre']

                if row['tipo']=="1":
                    print('TIPO 1')
                    tipo = "categoria"
                    categorias = odoo.env['catalogo.categoria']
                    datos = {
                        'name': str(row['descripcion']),
                        'descripcion': str(row['descripcion']),
                        'id_sideop': str(row['id'])
                    }
                    id_categoria = categorias.create(datos)
                    partidas_data = {'conceptos_partidas': [[0, 0, {
                                        'id_sideop': str(row['id']),
                                        'categoria': str(id_categoria),
                                        'id_partida': str(partida_),
                                        'clave_linea': str(row['clave']),
                                        #'concepto': str(row['descripcion']),
                                        'medida': str(row['unidad']),
                                        'cantidad':str(row['cantidad']),
                                        'precio_unitario': str(row['punitario'])
                                        }]] }

                    partida_seleccionada = partidas.browse(_search_partida[0])

                    partida_nueva = partida_seleccionada.write(partidas_data)

                if row['tipo']=="2":
                    print('TIPO 2')
                    tipo = "subcategoria"
                    categorias = odoo.env['catalogo.categoria']

                    _search_parent_id = odoo.env['catalogo.categoria'].search([("id_sideop","=",str(row['idpadre']))], limit=1)
                    print(_search_parent_id[0])
                    datos = {
                        'name': str(row['descripcion']),
                        'descripcion': str(row['descripcion']),
                        'id_sideop': str(row['id']),
                        'parent_id': str(_search_parent_id[0])
                    }
                    id_categoria = categorias.create(datos)

                    partidas_data = {
                                            'conceptos_partidas': [[0, 0, {
                                                                                    'id_sideop': str(row['id']),
                                                                                    'categoria': str(id_categoria),
                                                                                    'id_partida': str(partida_),
                                                                                    'clave_linea': str(row['clave']),
                                                                                    'concepto': str(row['descripcion']),
                                                                                    'medida': str(row['unidad']),
                                                                                    'cantidad':str(row['cantidad']),
                                                                                    'precio_unitario': str(row['punitario'])
                                                                                    }]] }
                    partida_seleccionada = partidas.browse(_search_partida[0])

                    partida_nueva = partida_seleccionada.write(partidas_data)
                    print('TERMINO TIPO 2')
                if row['tipo']=="3":
                    print('TIPO 3')
                    categoria = ""
                    tipo = "concepto"
                    categorias = odoo.env['catalogo.categoria']

                    _search_categoria = odoo.env['catalogo.categoria'].search([("id_sideop","=",str(row['idpadre']))], limit=1)
                    if len(_search_categoria)>0:
                        categoria = _search_categoria[0]

                    partidas_data = {
                                            'conceptos_partidas': [[0, 0, {
                                                                                    'id_sideop': str(row['id']),
                                                                                    'categoria': str(categoria),
                                                                                    'id_partida': str(partida_),
                                                                                    'clave_linea': str(row['clave']),
                                                                                    'concepto': str(row['descripcion']),
                                                                                    'medida': str(row['unidad']),
                                                                                    'cantidad':str(row['cantidad']),
                                                                                    'precio_unitario': str(row['punitario'])
                                                                                    }]] }
                    partida_seleccionada = partidas.browse(_search_partida[0])

                    partida_nueva = partida_seleccionada.write(partidas_data)
                    print('TERMINO TIPO 3')

                if row['idpadre']== False:
                    print("id padre en 0")

                idpadre = ""
                categoria = ""
                print("ok "+ tipo)

            except:
                print("error")