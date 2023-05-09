import odoorpc, csv
import datetime

usuario = 'admin'
password = 'admin'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('sidur2', usuario, password)

with open('contratos_convenios_modificatorios.csv', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        _search_part = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        _search_programa2 = odoo.env['partidas.partidas'].search_count(
            [("id_contrato_sideop", "=", row['num_contrato'])])

        if _search_programa2 == 0:
            print('NO EXISTE ESE CONTRATO', row['num_contrato'])

        else:
            print('SI EXISTE ESE CONTRATO', row['num_contrato'])

            _search_partidaid = odoo.env['partidas.partidas'].search(
                [("id_contrato_sideop", "=", row['num_contrato'])])

            print(_search_partidaid[0])

            convenio = odoo.env['proceso.convenios_modificado']

            if str(row['fecha']) == '':
                print('1')
                new_fecha = None
            else:
                new_fecha_ = str(row['fecha'])
                new_fecha = new_fecha_[6] + new_fecha_[7] + new_fecha_[8] + new_fecha_[9] + \
                             new_fecha_[5] + new_fecha_[3] + new_fecha_[4] + new_fecha_[2] + \
                             new_fecha_[0] + new_fecha_[1]

            if str(row['fecha_dictamen']) == '':
                print('2')
                new_fecha2 = None
            else:
                new_fecha2_ = str(row['fecha_dictamen'])
                new_fecha2 = new_fecha2_[6] + new_fecha2_[7] + new_fecha2_[8] + new_fecha2_[9] + \
                             new_fecha2_[5] + new_fecha2_[3] + new_fecha2_[4] + new_fecha2_[2] + \
                             new_fecha2_[0] + new_fecha2_[1]

            if str(row['fecha_fianza']) == '':
                print('3')
                new_fecha3 = None
            else:
                new_fecha3_ = str(row['fecha_fianza'])
                new_fecha3 = new_fecha3_[6] + new_fecha3_[7] + new_fecha3_[8] + new_fecha3_[9] + \
                             new_fecha3_[5] + new_fecha3_[3] + new_fecha3_[4] + new_fecha3_[2] + \
                             new_fecha3_[0] + new_fecha3_[1]

            if str(row['fecha_inicio']) == '':
                print('4')
                new_fecha4 = None
            else:
                new_fecha4_ = str(row['fecha_inicio'])
                new_fecha4 = new_fecha4_[6] + new_fecha4_[7] + new_fecha4_[8] + new_fecha4_[9] + \
                             new_fecha4_[5] + new_fecha4_[3] + new_fecha4_[4] + new_fecha4_[2] + \
                             new_fecha4_[0] + new_fecha4_[1]


            if str(row['fecha_termino']) == '':
                print('5')
                new_fecha5 = None
            else:
                new_fecha5_ = str(row['fecha_termino'])
                new_fecha5 = new_fecha5_[6] + new_fecha5_[7] + new_fecha5_[8] + new_fecha5_[9] + \
                                new_fecha5_[5] + new_fecha5_[3] + new_fecha5_[4] + new_fecha5_[2] + \
                                new_fecha5_[0] + new_fecha5_[1]

            if row['tipo'] == 'PL':
                print('PLAZO')

                datos_convenio = {
                    'contrato': _search_partidaid[0],
                    'id_sideop': row['id'],
                    'num_contrato_sideop': str(row['num_contrato']),

                    'tipo_convenio': row['tipo'],
                    'fecha_convenios': new_fecha,
                    'fecha_dictamen': new_fecha2,
                    'referencia': str(row['referencia']),
                    'observaciones': str(row['observaciones']),
                    'plazo_fecha_inicio': new_fecha4,
                    'plazo_fecha_termino': new_fecha5,
                    'objeto_nuevo_objeto': str(row['nuevo_objecto']),
                    'tipo_monto': row['tipo_monto'],
                    'monto_importe': row['importe'],
                    'convenio_numero_fianza': str(row['num_fianza']),
                    'convenio_fecha_fianza': new_fecha3,
                    'convenio_afianzadora': str(row['afianzadora']),
                    'convenio_monto_afianzadora': row['monto_fianza'],
                }
                convenios = convenio.create(datos_convenio)

            elif row['tipo'] == 'OB':
                print('OBJETO')
                datos_convenio = {
                    'contrato': _search_partidaid[0],
                    'id_sideop': row['id'],
                    'num_contrato_sideop': str(row['num_contrato']),

                    'tipo_convenio': row['tipo'],
                    'fecha_convenios': new_fecha,
                    'fecha_dictamen': new_fecha2,
                    'referencia': str(row['referencia']),
                    'observaciones': str(row['observaciones']),
                    'plazo_fecha_inicio': new_fecha4,
                    'plazo_fecha_termino': new_fecha5,
                    'objeto_nuevo_objeto': str(row['nuevo_objecto']),
                    'tipo_monto': row['tipo_monto'],
                    'monto_importe': row['importe'],
                    'convenio_numero_fianza': str(row['num_fianza']),
                    'convenio_fecha_fianza': new_fecha3,
                    'convenio_afianzadora': str(row['afianzadora']),
                    'convenio_monto_afianzadora': row['monto_fianza'],
                }
                convenios = convenio.create(datos_convenio)

            elif row['tipo'] == 'MT':
                print('MONTO')
                datos_convenio = {
                    'contrato': _search_partidaid[0],
                    'id_sideop': row['id'],
                    'num_contrato_sideop': str(row['num_contrato']),

                    'tipo_convenio': row['tipo'],
                    'fecha_convenios': new_fecha,
                    'fecha_dictamen': new_fecha2,
                    'referencia': str(row['referencia']),
                    'observaciones': str(row['observaciones']),
                    'plazo_fecha_inicio': new_fecha4,
                    'plazo_fecha_termino': new_fecha5,
                    'objeto_nuevo_objeto': str(row['nuevo_objecto']),
                    'tipo_monto': row['tipo_monto'],
                    'monto_importe': row['importe'],
                    'convenio_numero_fianza': str(row['num_fianza']),
                    'convenio_fecha_fianza': new_fecha3,
                    'convenio_afianzadora': str(row['afianzadora']),
                    'convenio_monto_afianzadora': row['monto_fianza'],
                }
                convenios = convenio.create(datos_convenio)

            elif row['tipo'] == 'BOTH':
                print('AMBOS')
                datos_convenio = {
                    'contrato': _search_partidaid[0],
                    'id_sideop': row['id'],
                    'num_contrato_sideop': str(row['num_contrato']),

                    'tipo_convenio': row['tipo'],
                    'fecha_convenios': new_fecha,
                    'fecha_dictamen': new_fecha2,
                    'referencia': str(row['referencia']),
                    'observaciones': str(row['observaciones']),
                    'plazo_fecha_inicio': new_fecha4,
                    'plazo_fecha_termino': new_fecha5,
                    'objeto_nuevo_objeto': str(row['nuevo_objecto']),
                    'tipo_monto': row['tipo_monto'],
                    'monto_importe': row['importe'],
                    'convenio_numero_fianza': str(row['num_fianza']),
                    'convenio_fecha_fianza': new_fecha3,
                    'convenio_afianzadora': str(row['afianzadora']),
                    'convenio_monto_afianzadora': row['monto_fianza'],
                }
                convenios = convenio.create(datos_convenio)
            else:
                print('ERROR')