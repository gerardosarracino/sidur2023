# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date
from datetime import datetime
import calendar
import warnings


class EstimacionesBis(models.Model):
    _inherit = 'control.estimaciones'

    estimacion_bis = fields.Many2one('control.estimaciones', string="Selecciona estimacion Bis")

    # SECCION DE ESTIMACION BIS
    # CALCULO DE LA ESTIMACION
    estimado_bis = fields.Float(string="Importe ejecutado estimación:", store=True, digits=(12, 2))

    estimado_bis_related = fields.Float('Estimado Bis', related="estimacion_bis.estimado")
    estimado_bis_actual = fields.Float('Estimado Bis Actual', store=True)
    estimado_bis_original = fields.Float('Estimado Bis Original', store=True)

    @api.multi
    @api.onchange('estimacion_bis')
    def estimado_original(self):
        self.estimado_bis_original = self.estimado_bis_related
        self.estimado_bis_actual = self.estimado_bis_related

    @api.multi
    @api.onchange('estimado_bis')
    def calculos_bis(self):
        self.estimado_bis_actual = self.estimado_bis_original - self.estimado_bis
        self.estimado = self.estimado_bis
        self.estimacion_subtotal = self.estimado_bis
        self.estimacion_iva = self.estimacion_subtotal * self.b_iva
        self.estimacion_facturado = self.estimacion_iva + self.estimacion_subtotal
        # SACAR VALOR DEDUCCIONES
        for rec in self.deducciones:
            rec.update({
                'valor': self.estimado * rec.porcentaje / 100
            })
            if self.tipo_estimacion == '3' or self.tipo_estimacion == '2':
                rec.update({
                    'valor': self.sub_total_esc_h * rec.porcentaje / 100
                })
        # SUMA DE DEDUCCIONES
        sumax = 0
        for i in self.deducciones:
            resultado = i.valor
            sumax = sumax + resultado
        self.estimado_deducciones = sumax
        self.a_pagar = self.estimacion_facturado - self.estimado_deducciones

