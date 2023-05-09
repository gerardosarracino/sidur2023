import odoorpc, csv
import datetime

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

with open('programa.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        _search_part = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        _search_programa = odoo.env['programa.programa_obra'].search_count(
            [("obra", "=", _search_part)])

        _search_programa2 = odoo.env['programa.programa_obra'].search(
            [("obra", "=", _search_part)])

        print(_search_programa)

        if _search_programa >= 1:
            prog = odoo.env['programa.programa_obra']
            # tabla programa
            s_datetime = datetime.datetime.strptime(row['Prog_Del'], '%Y%m%d')
            s_datetime2 = datetime.datetime.strptime(row['Prog_Al'], '%Y%m%d')

            _search_programa3 = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['num_contrato'])])

            datos_programa_est = {
                'programa_contratos': [[0, 0, {'id_prog': row['Prog_Id']
                                               , 'obra': _search_programa3[0]
                                            , 'fecha_inicio': str(s_datetime)
                                            , 'fecha_termino': str(s_datetime2)
                                            , 'monto': row['Prog_Monto']

                                               }]]
            }
            prog_seleccionada = prog.browse(_search_programa2[0])

            hacia_programa = prog_seleccionada.write(datos_programa_est)
            print('ya existe no paxa nada')

        else:
            print('no existe hay que crearlo')

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

                try:
                    part_prog = _search_programa3[0]
                    print(part_prog)
                    # obra_partida = _search_programa2.obra
                except:
                    print("error al buscar contrato" + str(row['num_contrato']))
                    pass

                datos_programa = {
                    'obra': _search_programa3[0],
                }

                programa = odoo.env['programa.programa_obra']

                id_programa = programa.create(datos_programa)

                programa_id = programa.browse(id_programa)
                # tabla programa
                s_datetime = datetime.datetime.strptime(row['Prog_Del'], '%Y%m%d')
                s_datetime2 = datetime.datetime.strptime(row['Prog_Al'], '%Y%m%d')
                datos_programa_est = {
                    'programa_contratos': [[0, 0, {'id_prog': row['Prog_Id']
                        , 'fecha_inicio': str(s_datetime)
                        , 'fecha_termino': str(s_datetime2)
                        , 'monto': row['Prog_Monto']

                                                   }]]
                }

                hacia_programa = programa_id.write(datos_programa_est)
