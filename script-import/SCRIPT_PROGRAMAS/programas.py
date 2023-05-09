import odoorpc, csv
import datetime
import mysql.connector
from datetime import date, datetime

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('35.223.0.35', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='35.223.0.35',
                              database='sideop_marzo')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `programa` ") # where num_contrato = 'SIDUR-ED-20-006.1878'

cursor.execute(query)

for row in cursor:
    _search_part = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=", row['num_contrato'])])

    _search_programa = odoo.env['programa.programa_obra'].search_count(
        [("obra", "=", _search_part)])

    _search_programa2 = odoo.env['programa.programa_obra'].search(
        [("obra", "=", _search_part)])

    print(row['num_contrato'], row['Prog_Id'])

    contrato = odoo.env['partidas.partidas']

    _search_contrato = odoo.env['partidas.partidas'].search(
            [("id_contrato_sideop", "=", row['num_contrato'])])

    b_contrato = contrato.browse(_search_contrato)

    programa = odoo.env['programa.programa_obra']
    b_p = programa.browse(_search_programa2)
    
    _search_programa2 = odoo.env['partidas.partidas'].search_count(
            [("id_contrato_sideop", "=", row['num_contrato'])])

    if _search_programa2 == 0:
        print('NO EXISTE ESE CONTRATO')

    else:
        print('SI EXISTE ESE CONTRATO')

        datos_programa = {
            'obra': b_contrato.id,
        }

        

        id_programa = b_p.write(datos_programa)
    
    '''if _search_programa >= 1:
        prog = odoo.env['programa.programa_obra']
        # tabla programa

        if len(str(row['Prog_Del'])) == '':
            print('1')
            Prog_Del = None
        else:
            Prog_Del_ = str(row['Prog_Del'])
            Prog_Del = Prog_Del_[4] + Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7] + '/' + Prog_Del_[0] + \
                        Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3]

        if len(str(row['Prog_Al'])) == '':
            print('1')
            Prog_Al = None
        else:
            Prog_Al_ = str(row['Prog_Al'])
            Prog_Al = Prog_Al_[4] + Prog_Al_[5] + '/' + Prog_Al_[6] + Prog_Al_[7] + '/' + Prog_Al_[0] + Prog_Al_[
                1] + Prog_Al_[2] + Prog_Al_[3]

        datos_programa_est = {
            'programa_contratos': [[0, 0, {'id_prog': row['Prog_Id']
                , 'obra': b_contrato.id
                , 'fecha_inicio': Prog_Del
                , 'fecha_termino': Prog_Al
                , 'monto': row['Prog_Monto']

                                        }]]
        }
        prog_seleccionada = prog.browse(_search_programa2[0])

        hacia_programa = prog_seleccionada.write(datos_programa_est)
        print('ya existe no paxa nada')

    else:
        print('no existe hay que crearlo')'''

        

    '''programa_id = programa.browse(id_programa)
            # tabla programa LAS FECHAS DEL SIDEOP ESTAN DELAV
            if len(str(row['Prog_Del'])) == '':
                print('1')
                Prog_Del = None
            else:
                Prog_Del_ = str(row['Prog_Del'])
                Prog_Del = Prog_Del_[4] + Prog_Del_[5] + '/' + Prog_Del_[6] + Prog_Del_[7] + '/' + Prog_Del_[0] + \
                        Prog_Del_[1] + Prog_Del_[2] + Prog_Del_[3]

            if len(str(row['Prog_Al'])) == '':
                print('1')
                Prog_Al = None
            else:
                Prog_Al_ = str(row['Prog_Al'])
                Prog_Al = Prog_Al_[4] + Prog_Al_[5] + '/' + Prog_Al_[6] + Prog_Al_[7] + '/' + Prog_Al_[0] + Prog_Al_[
                    1] + Prog_Al_[2] + Prog_Al_[3]

            datos_programa_est = {
                'programa_contratos': [[0, 0, {'id_prog': row['Prog_Id']
                    , 'fecha_inicio': Prog_Del
                    , 'obra': b_contrato.id
                    , 'fecha_termino': Prog_Al
                    , 'monto': row['Prog_Monto']

                                            }]]
            }

            hacia_programa = programa_id.write(datos_programa_est)'''


