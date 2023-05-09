import odoorpc, csv
import datetime

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

with open('estimaciones.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        _search_part = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        _search_estimacion = odoo.env['control.estimaciones'].search_count([("obra", "=", _search_part)])

        # _search_programa2 = odoo.env['programa.programa_obra'].search([("obra", "=", _search_part)])

        print(_search_estimacion)

        _search_programa2 = odoo.env['partidas.partidas'].search_count(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        if _search_programa2 == 0:
            print('NO EXISTE ESE CONTRATO')

        else:
            print('SI EXISTE ESE CONTRATO')

            _search_programa3 = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['num_contrato'])])

            print(_search_programa3[0])


            # part_prog = _search_programa3[0]

            if row['tipoEstimacion'] == '2':

                try:
                    part_prog = _search_programa3[0]
                    # obra_partida = _search_programa2.obra
                except:
                    print("error al buscar contrato" + str(row['num_contrato']))
                    pass

                estimaciones = odoo.env['control.estimaciones']
                print('es escalatoria')

                fecha_inicial_ = str(row['fechaInicial'])
                fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + \
                                fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + \
                                fecha_inicial_[0] + fecha_inicial_[1]

                fecha_final_ = str(row['fechaFinal'])
                fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[
                    5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

                fecha_presentacion_ = str(row['fechaPresentacion'])
                if str(row['fechaPresentacion']) == "":
                    fecha_presentacion = '0000/00/00'
                else:
                    fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                         fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                         fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + \
                                         fecha_presentacion_[1]

                fecha_revision_ = str(row['fechaRevisionResidente'])
                if str(row['fechaRevisionResidente']) == "":
                    fecha_revision = '0000/00/00'
                else:
                    fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[
                        9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + \
                                     fecha_revision_[0] + fecha_revision_[1]

                datos_programa = {
                    'obra': _search_programa3[0],
                    'id_sideop': row['id'],
                    'num_contrato': row['num_contrato'],
                    'tipo_estimacion': row['tipoEstimacion'],
                    'idobra': row['estimacion_escalatoria'],
                    'fecha_inicio_estimacion': fecha_inicial,
                    'fecha_termino_estimacion': fecha_final,
                    'fecha_presentacion': fecha_presentacion,
                    'fecha_revision': fecha_revision,
                    'estimacion_ids': str(estimacion_ids),
                }
                estimacion = estimaciones.create(datos_est)
                print(row['num_contrato'])
            else:
                print(row['num_contrato'])
                try:
                    part_prog = _search_programa3[0]
                    # obra_partida = _search_programa2.obra
                except:
                    print("error al buscar contrato" + str(row['num_contrato']))
                    pass

                estimaciones = odoo.env['control.estimaciones']
                print('es estimacion')

                # f_est_inicio_dia = datetime.datetime.strptime(row['fechaInicial'], '%Y%m%d')

                # print(f_est_inicio_dia)

                estimacion_ids = int(row['numEstimacion']) - 1

                fecha_inicial_ = str(row['fechaInicial'])
                fecha_inicial = fecha_inicial_[6] + fecha_inicial_[7] + fecha_inicial_[8] + fecha_inicial_[9] + fecha_inicial_[5] + fecha_inicial_[3] + fecha_inicial_[4] + fecha_inicial_[2] + fecha_inicial_[0] + fecha_inicial_[1]

                fecha_final_ = str(row['fechaFinal'])
                fecha_final = fecha_final_[6] + fecha_final_[7] + fecha_final_[8] + fecha_final_[9] + fecha_final_[5] + fecha_final_[3] + fecha_final_[4] + fecha_final_[2] + fecha_final_[0] + fecha_final_[1]

                fecha_presentacion_ = str(row['fechaPresentacion'])
                print(fecha_presentacion_)

                if str(row['fechaPresentacion']) == "":
                    print('NO HAY FECHA PRESENTACION')
                    fecha_presentacion = '2000/01/01'
                else:
                    fecha_presentacion = fecha_presentacion_[6] + fecha_presentacion_[7] + fecha_presentacion_[8] + \
                                         fecha_presentacion_[9] + fecha_presentacion_[5] + fecha_presentacion_[3] + \
                                         fecha_presentacion_[4] + fecha_presentacion_[2] + fecha_presentacion_[0] + fecha_presentacion_[1]
                    print(fecha_presentacion)
                fecha_revision_ = str(row['fechaRevisionResidente'])
                if str(row['fechaRevisionResidente']) == "":
                    print('NO HAY FECHA REVISION')
                    fecha_revision = '2000/01/01'
                else:
                    fecha_revision = fecha_revision_[6] + fecha_revision_[7] + fecha_revision_[8] + fecha_revision_[9] + fecha_revision_[5] + fecha_revision_[3] + fecha_revision_[4] + fecha_revision_[2] + fecha_revision_[0] + fecha_revision_[1]

                datos_est = {
                    'obra': str(_search_programa3[0]),
                    'id_sideop': str(row['id']),
                    'num_contrato': str(row['num_contrato']),
                    'tipo_estimacion': str(row['tipoEstimacion']),
                    'fecha_inicio_estimacion': str(fecha_inicial),
                    'fecha_termino_estimacion': str(fecha_final),
                    'fecha_presentacion': str(fecha_presentacion),
                    'fecha_revision': str(fecha_revision),
                    'estimacion_ids': str(estimacion_ids),
                    'notas': str(row['notas']),
                }

                estimacion = estimaciones.create(datos_est)
                # estimacion2 = estimaciones.write(datos_tabla)

                print(row['num_contrato'])