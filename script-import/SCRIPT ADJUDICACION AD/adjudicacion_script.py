import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('34.70.236.42', port=8069)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='navojoa2020',
                              host='34.70.236.42',
                              database='sidur')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `adjudicacion_directa` where id = '3'")

cursor.execute(query)

for row in cursor:
    adjudicacion = odoo.env['proceso.adjudicacion_directa']

    _search_adj = odoo.env['proceso.adjudicacion_directa'].search(
        [("id_sideop_adjudicacion", "=", row['id'])])

    b_adj = adjudicacion.browse(_search_adj)
    # p inv
    x = odoo.env['generales.programas_inversion']
    _search_x = odoo.env['generales.programas_inversion'].search(
        [("id_sideop", "=", row['prog_inv'])])
    b_x = x.browse(_search_x)

    # contratista
    c = odoo.env['contratista.contratista']
    _search_c = odoo.env['contratista.contratista'].search(
        [("id_sideop", "=", row['contratista'])])
    b_contra = c.browse(_search_c)

    if b_adj.id_sideop_adjudicacion == row['id']:
        print('ya existe pasar')
    else:
        print('no existe crear xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

        if len(str(row['fecha_adjudicacion'])) < 10:
            fecha_adjudicacion = None
        else:
            fecha_adjudicacion_ = str(row['fecha_adjudicacion'])
            fecha_adjudicacion = fecha_adjudicacion_[6] + fecha_adjudicacion_[7] + fecha_adjudicacion_[8] + fecha_adjudicacion_[9] + fecha_adjudicacion_[
                5] + fecha_adjudicacion_[3] + fecha_adjudicacion_[4] + fecha_adjudicacion_[2] + fecha_adjudicacion_[0] + fecha_adjudicacion_[1]

        if len(str(row['fecha_inicio'])) < 10:
            fecha_inicio = None
        else:
            fecha_inicio_ = str(row['fecha_inicio'])
            fecha_inicio = fecha_inicio_[6] + fecha_inicio_[7] + fecha_inicio_[8] + fecha_inicio_[9] + fecha_inicio_[
                5] + fecha_inicio_[3] + fecha_inicio_[4] + fecha_inicio_[2] + fecha_inicio_[0] + fecha_inicio_[1]

        if len(str(row['fecha_termino'])) < 10:
            fecha_termino = None
        else:
            fecha_termino_ = str(row['fecha_termino'])
            fecha_termino = fecha_termino_[6] + fecha_termino_[7] + fecha_termino_[8] + fecha_termino_[9] + fecha_termino_[
                5] + fecha_termino_[3] + fecha_termino_[4] + fecha_termino_[2] + fecha_termino_[0] + fecha_termino_[1]

        datos_adj = {
            'id_sideop_adjudicacion': row['id'],
            'name': row['meta'],
            'fechaadjudicacion': fecha_adjudicacion,
            'numerocontrato': row['num_contrato'],
            'programas_inversion_adjudicacion': b_x.id,
            'fechainicio': fecha_inicio,
            'fechatermino': fecha_termino,
            'plazodias': row['dias'],
            'normatividad': row['normatividad'],
            'contratista': b_contra.id,
            'anticipoinicio': float(row['anticipo_inicio']),
            'anticipomaterial': float(row['anticipo_material']),
            'dictamen': row['dictamen'],
        }
        # create = adjudicacion.create(datos_adj)

        print('exito')
