# -*- coding: utf-8 -*-
from odoo import http
import pandas as pd


class RegistroObras(http.Controller):
    @http.route('/registro_obras/registro_obras/', auth='public')
    def index(self, **kw):
        estimaciones = http.request.env['control.estimaciones']
        orden = estimaciones.sudo().search([('obra','=',kw['id'])])

        resultado = []
        obra = ''
        for i in orden:
            resultado.append(i.id)
            obra = i.obra.numero_contrato.contrato
            print(obra)

        # df1 = pd.DataFrame({'ID Estimación': resultado})
        df1 = pd.DataFrame({'ID Estimación': resultado, 'Obra': obra, 'C': 'fg', 'D': 'sdf', 'F': 'fgfg'})

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('/tmp/estimaciones.xlsx', engine='xlsxwriter')

        # Write each dataframe to a different worksheet.
        df1.to_excel(writer, sheet_name='Sheet1')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

        f = open('/tmp/estimaciones.xlsx', mode="rb")
        return http.request.make_response(f.read(),
                                          [('Content-Type', 'application/octet-stream'),
                                           ('Content-Disposition',
                                            'attachment; filename="{}"'.format('estimaciones.xls'))
                                           ])
        # return "Hello world "+kw['id']
