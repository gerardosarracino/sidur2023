import odoorpc, csv
import datetime
import mysql.connector

usuario = 'admin'
password = 'spiderboras'
odoo = odoorpc.ODOO('sidur.galartec.com', port=80)
odoo.login('SIDUR.OBRAS', usuario, password)

cnx = mysql.connector.connect(user='root', password='FENShFfnw7yuzF',
                              host='35.227.173.205',
                              database='sideop_febrero')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM `licitantes` INNER JOIN rep_legal ON licitantes.id = rep_legal.id_licitante")

cursor.execute(query)

for row in cursor:
    # BUSCAR CONTRATISTAS
    print(row['id'], '----- ',row['razon'])
    model_contratistas = odoo.env['contratista.contratista']

    contratista = odoo.env['contratista.contratista'].search([('id_sideop','=',row['id'])])
    b_c = model_contratistas.browse(contratista)

    if type(row['estado']) is not int:
        estadosxd = None
    elif type(row['estado']) is int:
        id_estado = row['estado']

        estados = odoo.env['generales.estado'].search([('id_sideop','=', id_estado)])

        estadosxd = odoo.env['generales.estado'].browse(estados)
        print(row['estado'])
        if type(estadosxd.id) is not int:
            print('xd')
            
        elif type(estadosxd.id) is int:
            print('xd2')
            estadosxd_ = odoo.env['generales.estado'].browse(estados)
            estadosxd = estadosxd.id
    

    if str(row['id']) == str(b_c.id_sideop):
        print('ya existe hacer cambios')
        '''campos_contratistas = { 'tipo_persona': row['tipo'],
                                'activo': row['status'],
                                'id_sideop': row['id'],
                                'name': row['razon'],
                                'nacionalidad': row['nacionalidad'],
                                'calles': row['calles'],
                                'colonia': row['colonia'],
                                'municipio_delegacion': row['municipo'],
                                'telefono': row['tel'],
                                'registro_concursante': row['registro'],
                                'rfc': row['rfc'],
                                'acreditacion_empresa': row['acreditacion'],
                                'numero': row['num_empresa'],
                                'cp': row['cp'],
                                'estado_entidad': estadosxd.id,
                                'correo': row['email'],
                                'objeto_social': row['objeto_emp'],
                                'nombre_representante': row['nombre'],
                                'rfc_representante_legal': row['rfc'],
                                'expedida_por': row['expedida'],
                                'caracter': row['caracter'],
                                'documento_acredita_nacionalidad': row['acreditacion'],
                                'numero_identificacion': row['ife'],
                            }

        form_contratistas = model_contratistas.write(campos_contratistas)
        print("ID contratista",form_contratistas)'''

    else:
        print('no existe crear')
        campos_contratistas = {'tipo_persona': row['tipo'],
                               'activo': row['status'],
                               'id_sideop': row['id'],
                               'name': row['razon'],
                               'nacionalidad': row['nacionalidad'],
                               'calles': row['calles'],
                               'colonia': row['colonia'],
                               'municipio_delegacion': row['municipo'],
                               'telefono': row['tel'],
                               'registro_concursante': row['registro'],
                               'rfc': row['rfc'],
                               'acreditacion_empresa': row['acreditacion'],
                               'numero': row['num_empresa'],
                               'cp': row['cp'],
                               'estado_entidad': estadosxd,
                               'correo': row['email'],
                               'objeto_social': row['objeto_emp'],
                               'nombre_representante': str(row['nombre']),
                               'rfc_representante_legal': row['rfc'],
                               'expedida_por': row['expedida'],
                               'caracter': row['caracter'],
                               'documento_acredita_nacionalidad': row['acreditacion'],
                               'numero_identificacion': row['ife'],
                               }

        form_contratistas = model_contratistas.create(campos_contratistas)
        print("ID contratista", form_contratistas)
       