# -*- coding: utf-8 -*-
{
    'name': "proceso_contratacion",

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
    'depends': ['base', 'informacion_basica', 'registro_obras', ],


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/licitacion.xml',
        'views/adjudicacion_directa.xml',
        'views/elaboracion_contrato.xml',
        'views/catalogo_conceptos.xml',
        'views/convenios_x.xml',
        'views/finiquitar_contrato_anticipadamente.xml',
        'views/anticipo.xml',
        'views/convenios.xml',
	'views/reporte_audisaf.xml',
    ],


    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],


}
