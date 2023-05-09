# -*- coding: utf-8 -*-
{
    'name': "ordenes_cambio",

    'summary': """
        ordenes de cambio""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sidur",
    'website': "http://sidur.galartec.com",

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
        'views/ordenes_cambio.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],


}
