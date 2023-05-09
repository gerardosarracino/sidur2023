import odoorpc, csv
import datetime
import mysql.connector
import subprocess
global ultimo_row


import time

def comienza(ultimo_row_OK):
    usuario = 'admin'
    password = 'spiderboras'
    odoo = odoorpc.ODOO('35.223.0.35', port=8069)
    odoo.login('SIDUR.OBRAS', usuario, password)

    cnx = mysql.connector.connect(user='root', password='navojoa2020',
                                host='35.223.0.35',
                                database='sidur',connect_timeout=100000)
    cursor = cnx.cursor(dictionary=True)

    query = ("SELECT * FROM `estimaciones_detalles` INNER JOIN catalogoconceptos ON estimaciones_detalles.id_concepto = catalogoconceptos.id where catalogoconceptos.id > "+str(ultimo_row_OK)+" order by catalogoconceptos.id asc;" )
    # "+str(ultimo_row_OK)+" 6784
    cursor.execute(query)
    
    for row in cursor:
        # print(str(ultimo_row_OK))
        try:
            try:
                contrato = odoo.env['partidas.partidas']
                estimaciones = odoo.env['control.estimaciones']

                print(row['num_contrato'], ' y la id es x', row['id'])

                _search_estimacion_count = odoo.env['control.estimaciones'].search_count(
                    [("num_contrato", "=", row['num_contrato'])])

                if _search_estimacion_count == 0:
                    print('NO EXISTE ESTA ESTIMACION', row['num_contrato'])
                else:
                    print('EXISTE ESTIMACION')

                    _search_estimacion = odoo.env['control.estimaciones'].search([("num_contrato", "=", row['num_contrato']), ("idobra", "=", row['num_estimacion']) ])
                    b_est = odoo.env['control.estimaciones'].browse(_search_estimacion[0])

                    if str(_search_estimacion2) == '[]':
                        pass
                    else:

                        print(row['num_estimacion'], "------" , b_est.idobra)

                        _search_partida = odoo.env['partidas.partidas'].search([("id_contrato_sideop", "=", row['num_contrato'])])
                        

                        _search_categoria = odoo.env['catalogo.categoria'].search([("id_sideop", "=", str(row['idpadre']))],
                                                                                limit=1)
                        
                        categorias = odoo.env['catalogo.categoria']

                        if str(_search_categoria) is not '[]':
                            categoriasx = _search_categoria
                            _search_cat = odoo.env['catalogo.categoria'].search(
                                [("id_sideop", "=", row['idpadre'])])
                            categoriax = categorias.browse(_search_cat)
                            categoria = categoriax.id
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

                        partida_seleccionada = estimaciones.browse(_search_estimacion[0])
                        
                        # partida_nueva = partida_seleccionada.write(datos_conceptos)
                        print(' al putazo')
    
            except:
                print('Fallo en '+str(row['num_contrato'])+ ' y la id es '+ str(row['id']))
                f = open('catalogoconceptos.txt', 'a') 
                f.write('Fallo en '+str(row['num_contrato'])+ ' y la id es '+ str(row['id'])+'\n')
                ultimo_row = row['id']
                f.close()
                f = open('ultimo_id.txt', 'w')
                f.write(str(row['id']))
                f.close()
            
        except:
            print('xd')
            subprocess.call("python3 estimaciones_conceptos_2020.py", shell=True)
try:
    f = open("ultimo_id.txt", "r")
    x = int(f.readline())
    f.close()
    comienza(x)
except:
    time.sleep(35)
    f = open("ultimo_id.txt", "r")
    x = int(f.readline())
    f.close()
    comienza(x)