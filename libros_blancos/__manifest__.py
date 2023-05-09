# -*- coding: utf-8 -*-
{
    'name': "Libros Blancos",

    'summary': """
        Libros Blancos""",

    'description': """
        Libros Blancos
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'proceso_contratacion', 'ejecucion_obra'],

    # always loaded
    'data': [
        'data/paperformat.xml',
        'views/revision_expedientes.xml',
        'views/entrega_documentacion.xml',
        'views/entrega_documentacion_2.xml',
        'views/revision_expedientes_libros.xml',
        
        'report/reporte.xml',
        'report/reporte_entrega.xml',
        'report/reporte_incidencia_conf.xml',
        'report/reporte_incidencia.xml',
        'report/reporte_conf.xml',
        'report/reporte_entrega_conf.xml',
    ],
}