import odoorpc, csv
import datetime
import mysql.connector
from datetime import datetime
import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                            host='sidur.galartec.com',
                            database='sidur') 
cursor = cnx.cursor(dictionary=True) 

query = (
    "SELECT soav.num_contrato AS num_contratoava, soav.NumeroAvance, soav.IdActividad, soav.Id AS idGeneral, soav.PorcentajeReal, soar.* FROM `soavances` soav INNER JOIN sorutacritica soar ON soav.num_contrato = soar.num_contrato AND soav.IdActividad = soar.Id where soav.num_contrato = 'SIDUR-ED-17-237.642' ORDER BY idGeneral asc") # where idGeneral <   where soav.num_contrato = 'SIDUR-PF-18-245.1494'

cursor.execute(query)
for row in cursor:
    print('LA ID ES xx', row['idGeneral'], 'y el contrato es x',row['num_contrato'], ' Y EL NUMERO DE AVANCE ES ', row['NumeroAvance'])

    if str(row['num_contrato']) == 'SIDUR-ED.-18-278.1551':
        numc = 'SIDUR-ED-18-278.1551'
    else:
        numc = row['num_contrato']

    numero_contrato_id = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", numc)])

    # Buscamos en informe de avance
    buscar_informe_avance = odoo.env['proceso.iavance'].search(
        [("numero_contrato", "=", numero_contrato_id), ("num_avance", "=", int(row['NumeroAvance']))])

    # print(buscar_informe_avance, ' INFORME --X-X-X-X-X-----')
    b_infor_c = odoo.env['proceso.iavance'].search_count(
        [("numero_contrato", "=", numero_contrato_id), ("num_avance", "=", int(row['NumeroAvance']))])

    if str(b_infor_c) == '0':
        print(' FALLO NOOO EXIIISTEEEE --X-X--X-X-X-X')
    else:
        
        buscar_informe_b = odoo.env['proceso.iavance'].browse(buscar_informe_avance)

        print(buscar_informe_b.numero_contrato.ejercicio.name)

        if str(buscar_informe_b.numero_contrato.ejercicio.name) == '2017':
            print('CREAR AQUIIIIIIII')

            partida = odoo.env['proceso.iavance']

            if str(row['PorcentajeReal']) == 'None' or str(row['PorcentajeEstimado']) == 'None' or str(row['PorcentajeReal']) == '0.0' or str(row['PorcentajeEstimado']) == '0.0':
                por_real = None
                porest = None
                por_avance = None
            else:
                por_real = float(row['PorcentajeReal'])
                porest = float(row['PorcentajeEstimado'])
                por_avance = float((por_real / porest)*100)

            datos_ruta = {

                'ruta_critica': [[0, 0,
                                    {
                                    'id_sideop': row['idGeneral'],
                                    'name': str(row['Nombre']),
                                    'porcentaje_est': str(row['PorcentajeEstimado']),
                                    'avance_fisico': por_avance,
                                    'numero_contrato': numero_contrato_id[0],
                                    'r': buscar_informe_b.id,
                                    'numero_informe': row['NumeroAvance'],
                                    }
                                    ]]
            }

            partida_seleccionada = partida.browse(buscar_informe_avance)
            hacia_rc = partida_seleccionada.write(datos_ruta)
            print('exito')
        else:
            print(' NO ES 2019 X-----X-X-X-X-X--X-X-X-X-X-X-X-X-X-')

    '''if str(buscar_informe_b.ruta_critica) == "Recordset('proceso.rc_a', [])":
        print('AGREGAR Y ACTUALIZAR -----------xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

        partida = odoo.env['proceso.iavance']

        if str(row['PorcentajeReal']) == 'None' or str(row['PorcentajeEstimado']) == 'None' or str(row['PorcentajeReal']) == '0.0' or str(row['PorcentajeEstimado']) == '0.0':
            por_real = None
            porest = None
            por_avance = None
        else:
            por_real = float(row['PorcentajeReal'])
            porest = float(row['PorcentajeEstimado'])
            por_avance = float((por_real / porest)*100)

        datos_ruta = {

            'ruta_critica': [[0, 0,
                                {
                                    'name': str(row['Nombre']),
                                    'porcentaje_est': por_real,
                                    'avance_fisico': por_avance,
                                    'numero_contrato': numero_contrato_id[0],
                                    'r': buscar_informe_b.id,
                                }]]
        }

        partida_seleccionada = partida.browse(buscar_informe_avance)
        hacia_rc = partida_seleccionada.write(datos_ruta)
        print('exito')'''

    '''if buscar_informe_avance == 0:

        print('NO EXISTE EL INFORME, PASAR')
    else:

        

        if str(row['num_contrato']) == str(buscar_informe_b.num_contrato):
            print('es el mismo contrato')

            partida = odoo.env['proceso.iavance']

            if str(row['PorcentajeReal']) == 'None' or str(row['PorcentajeEstimado']) == 'None' or str(row['PorcentajeReal']) == '0.0' or str(row['PorcentajeEstimado']) == '0.0':
                por_real = None
                porest = None
                por_avance = None
            else:
                por_real = float(row['PorcentajeReal'])
                porest = float(row['PorcentajeEstimado'])
                por_avance = float((por_real / porest)*100)

            datos_ruta = {

                'ruta_critica': [[0, 0,
                                  {
                                      'name': str(row['Nombre']),
                                      'porcentaje_est': por_real,
                                      'avance_fisico': por_avance,
                                      'numero_contrato': numero_contrato_id[0],
                                      'r': buscar_informe_b.id,
                                  }]]
            }

            partida_seleccionada = partida.browse(buscar_informe_avance)
            hacia_rc = partida_seleccionada.write(datos_ruta)
            print('exito')

        else:
            print('NO HAY :C')
'''