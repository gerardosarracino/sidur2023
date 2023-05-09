#!/usr/bin/python
# -*- coding: utf-8 -*-

import odoorpc, csv
import datetime

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

with open('rutacritica.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # CONTAR SI EXISTE LA PARTIDA PARA PODER PROSEGUIR
        _search_part = odoo.env['partidas.partidas'].search_count(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        # BUSCAR LA PARTIDA MISMA
        _search_part2 = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        print(_search_part)

        # SI EXISTE PARTIDA ENTONCES....
        if _search_part >= 1:

            print(row['num_contrato'])

            print('hay partida')
            # SI LA CONDICION DEL TIPO EN EL EXCEL ES IGUAL A UNO ENTONCES ES UN FRENTE
            if row['Tipo'] == '1':
                print('tipo 1')
                # BUSQUEDA EN LA CLASE DEL FRENTE MANY2ONE
                frente = odoo.env['proceso.frente']
                # VAMOS A BUSCAR EN LA PARTIDA
                partida2 = odoo.env['partidas.partidas']

                # crear FRENTE
                datos_frente = {'nombre': str(row['Nombre'])}
                # SE CREA EL FRENTE
                hacia_frente = frente.create(datos_frente)

                # VAMOS A BUSCAR EN LA PARTIDA
                tabla = odoo.env['partidas.partidas'] # EN EL ODOO LO QUE VIENE SIENDO PROGRAMA FRENTE DE TRABAJO
                # crear datos en tabla
                partidas_ruta2 = {'ruta_critica': [[0, 0, {
                                    'frente': str(hacia_frente),
                                    'id_partida': str(_search_part2[0]),
                                    'name': str(row['Nombre']),
                                    }]]}

                #
                tabla_seleccionada = partida2.browse(_search_part2[0])

                #tabla_creada = tabla_seleccionada.write(partidas_ruta2)

            # SI EL TIPO ES DOS ES ACTIVIDAD
            else:
                partida2 = odoo.env['proceso.rc']
                print('tipo 2')
                partida = odoo.env['partidas.partidas']

                datos_ruta = {

                    'ruta_critica': [[0, 0, {'name': str(row['Nombre']),
                    'frente': str(hacia_frente),
                    'id_partida': str(_search_part2[0]),
                    'porcentaje_est': str(row['PorcentajeEstimado'])
                                                }]]
                }
 
                partida_seleccionada = partida.browse(_search_part2[0])
                hacia_rc = partida_seleccionada.write(datos_ruta)


        # LA PARTIDA NO EXISTE
        else:
            print(row['num_contrato'])

            print('no existe este contrato')