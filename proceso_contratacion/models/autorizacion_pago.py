from odoo import api, fields, models
from num2words import num2words

class AutorizacionPago(models.Model):
    _name = "estimacion.autorizacion_pago"
    _rec_name = 'numero_factura'

    vinculo_estimaciones = fields.Many2one('control.estimaciones', string='Estimación id')  # ID DE ESTIMACION
    numero_contrato = fields.Many2one('partidas.partidas', string='Contrato', store=True)  # NUMERO DE CONTRATO DE PARTIDA
    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Contrato', store=True)  # NUMERO DE CONTRATO DE PARTIDA

    numero_factura = fields.Char('Numero de factura')
    fecha_factura = fields.Date('Fecha de Factura')

    numero_memo = fields.Char('Numero Memo')

    director_capturador = fields.Char('Director/Capturador', store=True) # iniciales en el footer del dierctor y capturador

    @api.multi
    @api.onchange('vinculo_estimaciones')
    def _numero_contrato_est(self):
        titular = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_titular')
        director_general_ejecucionobra = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_subdirector_obra')
        director_general_prog = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_director_prog')

        self.titular = titular
        self.director_ejecucion_obras = director_general_ejecucionobra
        self.director_programacion = director_general_prog
        if not director_general_ejecucionobra:
            pass
        else:
            # SACAR INICIALES DE DIRECTOR
            solo_nombre = director_general_ejecucionobra
            if director_general_ejecucionobra.split(' ', 1)[0] == "ING." or \
                    director_general_ejecucionobra.split(' ', 1)[0] == "ING" \
                    or director_general_ejecucionobra.split(' ', 1)[0] == "LIC." or \
                    director_general_ejecucionobra.split(' ', 1)[0] == "LIC.":
                solo_nombre = director_general_ejecucionobra.split(' ', 1)[1]
            line = solo_nombre
            words = line.split()
            letters = [word[0] for word in words]
            # SACAR INICIALES DE CAPTURADOR
            b_user = self.env['res.users'].browse(self.env.uid)
            line2 = b_user.name
            words2 = line2.split()
            letters2 = [word2[0] for word2 in words2]
            self.director_capturador = "".join(letters) + "/" + "".join(letters2)
            
        if not self.vinculo_estimaciones:
            pass
        else:
            self.numero_contrato = self.vinculo_estimaciones.obra.id
            self.contrato = self.vinculo_estimaciones.obra.numero_contrato.id
            self.programa_inversion = self.vinculo_estimaciones.obra.programaInversion
            self.contratista_contrato = self.vinculo_estimaciones.obra.contratista.id
            '''search_oficio = self.env['autorizacion_obra.anexo_tecnico'].search(
                [('concepto.id', '=', self.vinculo_estimaciones.obra.obra.id)])
            self.oficio_anexo = search_oficio.id
            self.inversion_anual_aut = search_oficio.total'''

            
            self.estimado = self.vinculo_estimaciones.estimado
            self.amort_anticipo = self.vinculo_estimaciones.amort_anticipo
            self.estimacion_subtotal = self.vinculo_estimaciones.estimacion_subtotal
            self.estimacion_iva = self.vinculo_estimaciones.estimacion_iva
            self.estimacion_facturado = self.vinculo_estimaciones.estimacion_facturado
            self.estimado_deducciones = self.vinculo_estimaciones.estimado_deducciones
            self.sancion = self.vinculo_estimaciones.sancion
            self.ret_neta_est = self.vinculo_estimaciones.ret_neta_est
            self.a_pagar = self.vinculo_estimaciones.a_pagar
            search_oficio = self.env['autorizacion_obra.anexo_tecnico'].search([('concepto.id', '=', self.obra.id)])

            for ofi in search_oficio:
                self.oficio_anexo = ofi.id
                self.inversion_anual_aut = ofi.total
                clave_string = ofi.clave_presupuestal.partition('-')
                clave_string2 = clave_string[2].partition('-')
                clave_string3 = clave_string2[2].partition('-')
                clave_string4 = clave_string3[2].partition('-')
                self.centro_gestor = clave_string[0]
                self.area_funcional = clave_string2[0]
                self.posicion_presupuestal = clave_string3[0]
                self.fondo = clave_string4[0]

            self.monto_letra_estimado = num2words(self.vinculo_estimaciones.a_pagar, lang='es')
            cent = str(round(self.vinculo_estimaciones.a_pagar, 2))
            self.centavos = str(cent)[-2:] + '/100'

            cent2 = str(cent[-2:].find("."))
            if str(cent2) == '0':
                x = str(cent2).replace(".", "0")
                self.centavos = x + str(self.estimacion_facturado)[-1:] + '/100'

            

            search_est = self.env['control.estimaciones'].search(
                [('obra.id', '=', self.numero_contrato.id)])
            acum_inv = 0
            for est in search_est:
                acum_inv += est.a_pagar
                if self.vinculo_estimaciones.id == est.id:
                    break

            self.inversion_ejercida = acum_inv
            self.saldo_por_ejercer = self.numero_contrato.total_civa - self.inversion_ejercida

    @api.multi
    @api.onchange('numero_contrato')
    def _numero_contrato(self):
        titular = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_titular')
        director_general_ejecucionobra = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_responsable_licitacion')
        director_general_prog = self.env['ir.config_parameter'].sudo().get_param('firmas_logos.nombre_director_prog')
        if not director_general_ejecucionobra:
            pass
        else:
            solo_nombre = director_general_ejecucionobra
            if director_general_ejecucionobra.split(' ', 1)[0] == "ING." or \
                    director_general_ejecucionobra.split(' ', 1)[0] == "ING" \
                    or director_general_ejecucionobra.split(' ', 1)[0] == "LIC." or \
                    director_general_ejecucionobra.split(' ', 1)[0] == "LIC.":
                solo_nombre = director_general_ejecucionobra.split(' ', 1)[1]

            line = solo_nombre
            words = line.split()
            letters = [word[0] for word in words]
            # SACAR INICIALES DE CAPTURADOR
            b_user = self.env['res.users'].browse(self.env.uid)
            line2 = b_user.name
            words2 = line2.split()
            letters2 = [word[0] for word in words2]
            self.director_capturador = "".join(letters) + "/".join(letters2)

        self.titular = titular
        self.director_ejecucion_obras = director_general_ejecucionobra
        self.director_programacion = director_general_prog
        if not self.numero_contrato:
            pass
        else:
            self.contrato = self.numero_contrato.numero_contrato.id
            self.programa_inversion = self.numero_contrato.programaInversion.id
            self.contratista_contrato = self.numero_contrato.contratista.id
            search_oficio = self.env['autorizacion_obra.anexo_tecnico'].search(
                [('concepto.id', '=', self.numero_contrato.obra.id)])
            if not search_oficio:
                pass
            else:
                self.estimado = self.numero_contrato.anticipo_a
                self.amort_anticipo = 0
                self.estimacion_iva = self.numero_contrato.iva_anticipo
                self.estimacion_facturado = self.numero_contrato.total_anticipo
                self.a_pagar = self.numero_contrato.total_anticipo

                self.monto_letra_estimado = num2words(round(self.numero_contrato.total_anticipo, 2), lang='es')
                cent = str(round(self.numero_contrato.total_anticipo, 2))
                self.centavos = str(cent)[-2:] + '/100'

                cent2 = str(cent[-2:].find("."))
                if str(cent2) == '0':
                    x = str(cent2).replace(".", "0")
                    self.centavos = x + str(self.estimacion_facturado)[-1:] + '/100'

                for ofi in search_oficio:
                    self.oficio_anexo = ofi.id
                    self.inversion_anual_aut = ofi.total
                    clave_string = ofi.clave_presupuestal.partition('-')
                    clave_string2 = clave_string[2].partition('-')
                    clave_string3 = clave_string2[2].partition('-')
                    clave_string4 = clave_string3[2].partition('-')
                    self.centro_gestor = clave_string[0]
                    self.area_funcional = clave_string2[0]
                    self.posicion_presupuestal = clave_string3[0]
                    self.fondo = clave_string4[0]
        if self.tipo_pago == 'Pago':
                self.anticipo_texto = "Anticipo"

    monto_letra_estimado = fields.Char(string="", store=True )
    centavos = fields.Char(string="", store=True )
    centro_gestor = fields.Char(string="", store=True )
    area_funcional = fields.Char(string="", store=True )
    posicion_presupuestal = fields.Char(string="", store=True )
    fondo = fields.Char(string="", store=True )
    titular = fields.Char(string="", store=True )
    director_ejecucion_obras = fields.Char(string="Director de Ejecucion de Obras", store=True )
    director_programacion = fields.Char(string="Director General de programacion", store=True )

    autorizacion_pago = fields.Char(string='Autorizacion de Pago No.', store=True)
    programa_inversion = fields.Many2one('generales.programas_inversion', required=True, string='Fondo')

    fecha = fields.Date(string='Fecha de autorizacion', )

    fecha_inicio_est = fields.Date(string='Fecha inicio de estimacion', related="vinculo_estimaciones.fecha_inicio_estimacion")
    fecha_termino_est = fields.Date(string='Fecha termino de estimacion', related="vinculo_estimaciones.fecha_termino_estimacion")

    num_estimacion = fields.Char('# Estimacion', related="vinculo_estimaciones.idobra")

    deducciones = fields.Many2many('control.deducciones', string="Deducciones:", related="vinculo_estimaciones.deducciones")

    contratista_contrato = fields.Many2one('contratista.contratista', store=True)
    obra = fields.Many2one(string='Obra:', readonly=True, related="numero_contrato.obra")  # OBRA DE LA PARTIDA

    convenio_asignacion = fields.Many2one('proceso.convenios_modificado', string="Asignación")

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", )

    oficio_anexo = fields.Many2one(comodel_name="autorizacion_obra.anexo_tecnico", string="Oficio", store=True)

    # CAMPOS ESTIMADOS

    estimado = fields.Float(string="Importe ejecutado estimación:", store=True, digits=(12, 2))
    amort_anticipo = fields.Float(string="Amortización de Anticipo:", compute="amortizacion_anticipo", store=True, digits=(12, 2))
    estimacion_subtotal = fields.Float(string="Neto Estimación sin IVA:", store=True, digits=(12, 2))
    estimacion_iva = fields.Float(string="I.V.A. 16%", store=True, digits=(12, 2))
    estimacion_facturado = fields.Float(string="Neto Estimación con IVA:", store=True, digits=(12, 2))
    estimado_deducciones = fields.Float(string="Menos Suma Deducciones:", store=True, digits=(12, 2))
    sancion = fields.Float(string="Sanción por Incump. de plazo:", digits=(12, 2),store=True)
    ret_neta_est = fields.Float(string='Retenciones', store=True, digits=(12, 2))
    a_pagar = fields.Float(string="Importe liquido:", store=True, digits=(12, 2))

    inversion_anual_aut = fields.Float('Inversion anual autorizada', digits=(12, 2))
    inversion_ejercida = fields.Float('Inversion ejercida', digits=(12, 2))
    saldo_por_ejercer = fields.Float('Saldo por ejercer', digits=(12, 2))

    '''@api.onchange('autorizacion_pago') PARA DESPUES TALVEZ
    def actualizar_autorizacion(self):
        if not self.autorizacion_pago:
            pass
        else:
            b_est = self.env['control.estimaciones'].browse(self.vinculo_estimaciones.id)
            dato = {
                'con_autorizacion': True
            }
            listax = b_est.write(dato)'''

    # AGREGAR PAGO FINIQUITO
    radio_pago = [(
        'Estimacion', "Estimacion"), ('Pago', "Pago de Anticipo")]
    tipo_pago = fields.Selection(radio_pago, string="Tipo de Pago")
    anticipo_texto = fields.Char(string="Anticipo", store=True )

