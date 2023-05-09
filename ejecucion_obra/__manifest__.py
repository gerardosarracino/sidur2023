# -*- coding: utf-8 -*-
{
    'name': "ejecucion_obras",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'informacion_basica', 'proceso_contratacion', 'autorizacion_obra', 'registro_obras'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/programa.xml',
        'views/control_estimaciones.xml',
        # 'views/supervision_obra.xml',
        'views/templates.xml',
        'views/convenios.xml',
        'views/autorizacion_pago.xml',
        'data/paperformat.xml',
        'data/paperformat_estimacion.xml',
        # 'report/estado_de_cuenta.xml',
        'report/reporte_control_est.xml',
        'report/reporte_relacion_conceptos.xml',
        'report/reporte_penas_convencionales.xml',
        'report/estimacion_concentrado.xml',
        # 'report/estado_cuenta_report.xml',
        'views/galeria_imagenes.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'css': ['static/src/css/size_tree.css'],
}
