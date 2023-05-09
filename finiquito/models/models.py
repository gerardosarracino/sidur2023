# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partidas(models.Model):
    _name = 'finiquito.partidas'
    _inherit = 'partidas.partidas'

    finiquito = fields.Selection([('0', 'No Finiquitado'),('1', 'Finiquitado'),], default='0')

class finiquito(models.Model):
    _name = 'finiquito.finiquitado'

    name = fields.Many2one('finiquito.partidas', readonly=True)
    fecha1 = fields.Date(string="Fecha de aviso de terminación de los trabajos")
    fecha2 = fields.Datetime(string="Fecha y hora verificación de la terminación de los trabajos")
    numero = fields.Char(string="Número bitácora del contrato", required=True)
    nota1 = fields.Text(string="Nota de bitácora aviso terminación")
    fecha3 = fields.Date(string="Fecha nota bitácora")
    fecha4 = fields.Date(string="Fecha de aviso de terminación de trabajos")
    fecha5 = fields.Date(string="Fecha de inicio Real del contrato")
    fecha6 = fields.Date(string="Fecha de termino real del contrato")
    fecha7 = fields.Datetime(string="Fecha y hora programada del acta de recepción de los trabajos")
    fecha8 = fields.Datetime(string="Fecha y hora entrega de la obra")
    fecha9 = fields.Datetime(string="Fecha y hora finiquito")
    fecha10 = fields.Datetime(string="Fecha y hora acta cierre administrativo")
    fecha11 = fields.Datetime(string="Fecha y hora acta de extinción de derechos")
    description = fields.Text(string="Descripción de los trabajos")
    ceditosContra = fields.Char(string="Créditos en contra del contratista al finalizar la obra")
    
    @api.multi
    def reporte_finiquito(self):
        original_url = "http://sidur.galartec.com/documento/finiquito/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
               }    