# -*- coding: utf-8 -*-
{
    'name': "Control de Expediente",

    'summary': """
        Control de expedientes""",

    'description': """
        Control de los expedientes
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
        'security/ir.model.access.csv',
        'views/control_expediente.xml',
        'views/control_expediente_contrato.xml',
    ],
}