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

query = ("SELECT * FROM `contratos` where numero_contrato = 'SIDUR-ED-16-353'")

cursor.execute(query)

for row in cursor:
    print(row['num_contrato'])
    tipo_contrato = "1"

    _search_contrato = odoo.env['proceso.elaboracion_contrato'].search_count(
        [("contrato", "=", row['numero_contrato'])])

    if _search_contrato == 0:
        print('no existe xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    else:

        contra = odoo.env['proceso.elaboracion_contrato']

        _search_contratox = odoo.env['proceso.elaboracion_contrato'].search(
            [("contrato", "=", row['numero_contrato'])])

        b_contrato = contra.browse(_search_contratox)

        if b_contrato.anexos:
            print('si existe')
        else:
            print('no existe')
        

            if str(b_contrato.tipo_contrato) == '2':
                print('es lici')
                for i in b_contrato.contrato_partida_adjudicacion:

                    anexox = odoo.env['autorizacion_obra.anexo_tecnico']
                    b_anexo_adju = odoo.env['autorizacion_obra.anexo_tecnico'].search([('id', '=', i.recursos.id)])
                    b_anex = anexox.browse(b_anexo_adju)


                    datos_anexo = {
                        'anexos': [[0, 0, {'name': b_anex.name.id, 'claveobra': b_anex.claveobra,
                                        'id_contrato': b_contrato.id,
                                        'clave_presupuestal': b_anex.clave_presupuestal,
                                        'federal': b_anex.federal,
                                        'concepto': b_anex.concepto.id,
                                        'estatal': b_anex.estatal,
                                        'municipal': b_anex.municipal, 'otros': b_anex.otros,
                                        'ferderalin': b_anex.federalin, 'estatalin': b_anex.estatalin,
                                        'municipalin': b_anex.municipalin, 'otrosin': b_anex.otrosin,
                                        'total': b_anex.total, 'cancelados': b_anex.cancelados,
                                        'total_ca': b_anex.total_ca,
                                        'total1': b_anex.total1, 'totalin': b_anex.totalin,
                                        'total_at': b_anex.total_at,
                                        }]]
                    }
                    print('awebo')
                    # partida_al_contrato = b_contrato.write(datos_anexo)
                print('termino')

            # licitacion
            elif str(b_contrato.tipo_contrato) == '1':
                print('es adjudicacion')
                for i in b_contrato.contrato_partida_licitacion:
                    print('si llego aqui')
                    anexox = odoo.env['autorizacion_obra.anexo_tecnico']
                    b_anexo_lici = odoo.env['autorizacion_obra.anexo_tecnico'].search([('id', '=', i.recursos.id)])

                    b_anex = anexox.browse(b_anexo_lici)

                    datos_anexo = {
                        'anexos': [[0, 0, {'name': b_anex.name.id, 'claveobra': b_anex.claveobra,
                                        'id_contrato': b_contrato.id,
                                        'clave_presupuestal': b_anex.clave_presupuestal,
                                        'federal': b_anex.federal,
                                        'concepto': b_anex.concepto.id,
                                        'estatal': b_anex.estatal,
                                        'municipal': b_anex.municipal, 'otros': b_anex.otros,
                                        'ferderalin': b_anex.federalin, 'estatalin': b_anex.estatalin,
                                        'municipalin': b_anex.municipalin, 'otrosin': b_anex.otrosin,
                                        'total': b_anex.total, 'cancelados': b_anex.cancelados,
                                        'total_ca': b_anex.total_ca,
                                        'total1': b_anex.total1, 'totalin': b_anex.totalin,
                                        'total_at': b_anex.total_at,
                                        }]]
                    }
                    print('awebo')
                    # partida_al_contrato = b_contrato.write(datos_anexo)
                print('termino')
                        # partida_al_contrato = contrato_id.write(datos_partida)
