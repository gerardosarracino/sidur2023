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

# query = ("SELECT * FROM `participantes_licitacion` INNER JOIN licitantes ON participantes_licitacion.id_licitante = licitantes.id")
query = ("SELECT * FROM `participantes_licitacion` INNER JOIN licitantes ON participantes_licitacion.id_licitante = licitantes.id order by licitantes.id desc")

cursor.execute(query)

for row in cursor:
    print(row['id'], 'ids' ,row['id_licitacion'],)

    participante = odoo.env['proceso.participante']
    lici = odoo.env['proceso.licitacion']
    contratista = odoo.env['contratista.contratista']

    _search_parti = odoo.env['proceso.participante'].search(
        [("id_sideop", "=", row['id_licitacion'])])

    _search_lici = odoo.env['proceso.licitacion'].search(
        [("numerolicitacion", "=", row['id_licitacion'])])

    _search_contra = odoo.env['contratista.contratista'].search(
        [("id_sideop", "=", row['id_licitante'])])

    b_parti = participante.browse(_search_parti)
    b_lici = lici.browse(_search_lici)
    b_contra = contratista.browse(_search_contra)

    '''if int(row['id']) == int(b_parti.id_sideop):
        print('YA EXISTE PARTICIPANTES')

        datos_participantes = {

            'contratista_participante': [[1, b_contra.id, {
                'name': b_contra.id,
            }]]}

        x = participante.browse(b_parti.id)

        parti = x.update(datos_participantes)'''

    _search_partix = odoo.env['proceso.participante'].search_count(
        [("id_sideop", "=", row['id_licitacion'])])

    if _search_partix >= 1:
        print('ya existe actualizamos tabla')
        datos_participantes = {
            'contratista_participantes': [[4, b_contra.id
            ]]}

        x = participante.browse(b_parti.id)

        parti = x.update(datos_participantes)
        
    else:
        
        print(b_contra.id)
        print(b_contra.name)
        datos_lici = {
            'id_sideop': row['id_licitacion'],
            'numerolicitacion': b_lici.id,
             'contratista_participantes': [[4, b_contra.id
            ]]
        }
        
        part = participante.create(datos_lici)

        print('exito')
        

