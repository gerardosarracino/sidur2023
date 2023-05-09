# -*- coding: utf-8 -*-
{
    'name': "report estimaciones",

    'summary': """
       report estimaciones""",

    'description': """
        bienvenido a report report_estimaciones
    """,

    'author': "Biblioteca inc.",
    'website': "http://www.biblioinc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ejecucion_obra'],

    # always loaded
    'data': [
        'data/paperformat.xml',
        'data/paperformat_pago.xml',
        'report/control_estimaciones_report.xml',
        'report/reporte_control_est.xml',
        'report/relacion_conceptos_report.xml',
        'report/reporte_relacion_conceptos.xml',
        'report/reporte_penas_convencionales.xml',
        'report/penas_convencionales_report.xml',
        'report/estimacion_concentrado_report.xml',
        'report/estimacion_concentrado.xml',
        'report/modelo_factura_conf.xml',
        'report/modelo_factura_report.xml',
        'report/autorizacion_pago.xml',
        'report/config_autorizacion_pago.xml',
       
        'report/report_memo.xml',
        'report/estimacion_tramite_report.xml',
        'report/config_estimacion_tramite.xml',
        'report/estimacion_escalatoriamultiple_report.xml',
        'report/estimacion_escalatoriamultiple_config.xml',
    ],
    # only loaded in demonstration mode
   'installable': True,
}