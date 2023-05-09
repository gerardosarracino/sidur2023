import odoorpc, csv
import datetime
import mysql.connector
from datetime import datetime
import time

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=8069)
odoo.login('sidur2020', usuario, password)

cnx = mysql.connector.connect(user='root', password='Navojoa2020',
                            host='sidur.galartec.com',
                            database='sideop_marzo') 
cursor = cnx.cursor(dictionary=True) 


query = ("SELECT c.num_contrato, f.nombre_funcionario FROM contratos c inner join funcionarios f on c.id_residente = f.id")
# where num_contrato = 'SIDUR-ED-20-006.1878'
cursor.execute(query)

for row in cursor:
    '''if row['tipo_procedimiento'] == "AD":'''

    # print(row['numero_contrato'])

    contra = odoo.env['proceso.elaboracion_contrato']
    
    '''_search_contratox = odoo.env['proceso.elaboracion_contrato'].search(
            [("contrato", "=", row['numero_contrato'])])

    b_contrato = contra.browse(_search_contratox)'''

    '''if str(_search_contratox) == '[]':
        print('NO EXISTE')
    else:'''
    print('dale con todo')
    # part_adj = odoo.env['partidas.adjudicacion']

    '''_search_partadj = odoo.env['partidas.adjudicacion'].search(
            [("id_adjudicacion", "=", int(b_contrato.adjudicacion.id))])

    b_partadj = part_adj.browse(_search_partadj)

    print(_search_partadj)'''
    
    '''if str(_search_partadj) == '[]':
        print('NO EXISTE')'''
    # else:
    partidas = odoo.env['partidas.partidas']

    c = odoo.env['proceso.elaboracion_contrato']

    programa = odoo.env['registro.programarobra']

    _search_part = odoo.env['partidas.partidas'].search(
        [("id_contrato_sideop", "=",row['num_contrato'])])

    '''_search_programa = odoo.env['registro.programarobra'].search(
        [("Id_obraprogramada", "=",row['id_partida'])])'''

    b_part = partidas.browse(_search_part)

    # b_contra = c.browse(_search_contratox)

    # b_prog = programa.browse(_search_programa)

    # print(_search_part, ' partida encotnradaddaa')

    '''eje = odoo.env['registro.ejercicio']
    b_eje = odoo.env['registro.ejercicio'].search([("name", "=", str(row['ejercicio']))])
    b_ejercicio = eje.browse(b_eje)'''

    '''if len(str(row['fecha'])) < 10:
        fecha = None
    else:
        fecha_ = str(row['fecha'])
        fecha = fecha_[6] + fecha_[7] + fecha_[8] + \
                fecha_[9] + fecha_[
                    5] + fecha_[3] + fecha_[4] + fecha_[2] + \
                fecha_[0] + fecha_[1]
    
    if len(str(row['fecha_inicio'])) < 10:
        fecha2 = None
    else:
        fecha2_ = str(row['fecha_inicio'])
        fecha2 = fecha2_[6] + fecha2_[7] + fecha2_[8] + \
                fecha2_[9] + fecha2_[
                    5] + fecha2_[3] + fecha2_[4] + fecha2_[2] + \
                fecha2_[0] + fecha2_[1]
    
    if len(str(row['fecha_termino'])) < 10:
        fecha3 = None
    else:
        fecha3_ = str(row['fecha_termino'])
        fecha3 = fecha3_[6] + fecha3_[7] + fecha3_[8] + \
                fecha3_[9] + fecha3_[
                    5] + fecha3_[3] + fecha3_[4] + fecha3_[2] + \
                fecha3_[0] + fecha3_[1]'''

    # print('si entrooooooooooooo')
    datos_partida = {
        'residente_x': row['nombre_funcionario'],
        # 'fecha': fecha,
        # 'fechainicio': fecha2,
        # 'fechatermino': fecha3,
        # 'numero_contrato': b_part.id,
        # 'ejercicio': b_ejercicio.id,
        # 'municipio': b_prog.obra_planeada.municipio.id,
        # 'programaInversion': b_prog.programaInversion.id,
        # 'nombre_contrato': row['numero_contrato']
        }
        
    # print(b_partadj.obra.descripcion)
    print(row['num_contrato'])
    # x = partidas.browse(b_part.id)
    # print(b_prog.id_sideop)
    actua = b_part.write(datos_partida)
    print('exito')
    # print(b_partadj.obra.descripcion)
