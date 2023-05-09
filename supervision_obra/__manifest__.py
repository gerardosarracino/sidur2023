# -*- coding: utf-8 -*-
{
    'name': "supervision_obra",

    'summary': """
        SUPERVISION DE OBRA SIDUR""",

    'description': """
        MODULO DE SUPERVISORES
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
        #'views/control_estimaciones.xml',
        'views/supervision_obra.xml',
        # 'views/convenios.xml',
        # 'views/galeria_imagenes.xml',
        # 'views/catalogo_conceptos.xml',
        'views/control_expediente.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'css': ['static/src/css/size_tree.css'],
}
