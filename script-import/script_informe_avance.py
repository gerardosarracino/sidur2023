import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('35.238.206.12', port=8069)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='34.70.236.42',
                              database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `soavancesgeneral`" )

cursor.execute(query)

for row in cursor:
    print(row['Id'], row['num_contrato'])
    numero_contrato_id = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    # CONTAR SI EXISTE LA PARTIDA PARA PODER PROSEGUIR
    buscar_partida = odoo.env['partidas.partidas'].search_count(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    #Buscamos en informe de avance
    buscar_informe_avance = odoo.env['proceso.iavance'].search_count(
        [("num_contrato", "=", row['num_contrato']),("NumeroAvance","=",row['NumeroAvance'])])
    print(buscar_informe_avance)
    # print("No se encontro partida",buscar_partida)

    if buscar_informe_avance == 0:

        print('NO EXISTE EL INFORME, CREAR DATOS DE INFORME')

        avance = odoo.env['proceso.iavance']
        fecha_act = datetime.datetime.strptime(row['FechaAvance'], '%Y%m%d')

        campos_ia = {'situacion_contrato.id':  row['SituacionContrato'],
                        'fecha_actual': str(fecha_act),
                        'com_avance_obra': str(row['ComentarioAvance']),
                        'numero_contrato': numero_contrato_id[0], 
                        'num_contrato': str(row['num_contrato']),
                        'sideop_id_rt': int(row['Id_import']),
                        'NumeroAvance': int(row['NumeroAvance']),
                        } # CHECAR EL EXCEL NULL

        form_ia = avance.create(campos_ia)
        print(form_ia) 

    else:
        print('si existe')

        if row['Tipo'] == '1':
            frente = row['Nombre']
            print("es frente")
        else:
            print("es actividad")
            buscar_informe_avance2 = odoo.env['proceso.iavance'].search(
                [("num_contrato", "=", row['num_contrato']),("NumeroAvance","=",row['NumeroAvance'])])

            buscar_informe_b = odoo.env['proceso.iavance'].browse(buscar_informe_avance2)
            
            print("numero de contrato",row['num_contrato'])
            print(buscar_informe_b.sideop_id_rt)
            print(row['Id_import'])

            if str(row['num_contrato']) == str(buscar_informe_b.num_contrato):
                print('es el mismo contrato')

                # if str(buscar_informe_b.sideop_id_rt) == str(row['Id_import']):
                    # print('crear datos tabla')

                partida = odoo.env['proceso.iavance']

                datos_ruta = {

                    'ruta_critica': [[0, 0, 
                    {'name': str(row['Nombre']),
                    'avance_fisico':  float(row['AvFis']),
                    'frente': frente,
                    'porcentaje_est': float(row['PorcentajeEstimado'])
                                                }]]
                }

                partida_seleccionada = partida.browse(buscar_informe_avance2)
                hacia_rc = partida_seleccionada.write(datos_ruta)
            else:
                print('NO HAY :C')
