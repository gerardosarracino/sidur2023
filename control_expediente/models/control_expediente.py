from odoo import models, fields, api, exceptions


class ControlExpedienteContrato(models.Model):
    _name = 'control.expediente_contrato'
    _rec_name = 'contrato_id'

    contrato_id = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Contrato", required=True)

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", )
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra",)

    # RELATED
    total_contrato = fields.Float('Total Contrato s/iva', related="contrato_id.total_contratado_modificado")
    obra = fields.Text(related="contrato_id.name")
    fechainicio = fields.Date(string="Fecha de Inicio", related="contrato_id.fechainicio")
    fechatermino = fields.Date(string="Fecha de Termino", related="contrato_id.fechatermino")
    contratista = fields.Many2one('contratista.contratista', related="contrato_id.contratista")

    tabla_control = fields.Many2many('control.expediente', )

    @api.multi
    def agregar_expedientes(self): # ACTUALIZAR LISTA
        if self.tabla_control:
            pass
        else:
            b_contrato = self.env['proceso.elaboracion_contrato'].search([('id', '=', self.contrato_id.id)])
            var = ''
            if b_contrato.adjudicacion:  # ADJUDICACION
                if b_contrato.adjudicacion.normatividad == '1':  # 1 = federal
                    var = 'Adjudicación Federal'
                else:  # estatal
                    var = 'Adjudicación Estatal'
            else:  # LICITACION
                if b_contrato.obra.tipolicitacion == '1':  # 1 = LIC PUBLICA
                    if b_contrato.obra.normatividad == '1':  # FEDERAL
                        var = 'Licitación Publica Federal'
                    else:  # ESTATAL
                        var = 'Licitación Publica Estatal'
                else:  # LIC SIMPLIFICADA
                    if b_contrato.obra.normatividad == '1':  # FEDERAL
                        var = 'Licitación Simplificada Estatal'
                    else:  # ESTATAL
                        var = 'Licitación Simplificada Federal'

            b_expediente = self.env['control_expediente.control_expediente'].search(
                [('tipo_expediente.tipo_expediente', '=', var)],
                order='orden asc')
            numeracion = 0
            for vals in b_expediente:
                numeracion += 1
                print(numeracion)
                datos = {'tabla_control':
                             [[0, 0,
                               {
                                   'numeracion': numeracion,
                                   'orden': vals.orden,
                                   'nombre': vals.id,
                                   'nombre_documento': vals.nombre,
                                   'contrato_id': b_contrato.id,
                                   'auxiliar': False,
                                   'id_documento_categoria': None,
                                   'auxiliar_comprimido': False,
                                   'auxiliar_documentos_categoria': False,
                                   'auxiliar_documentos_categoria2': False,
                                   'p_id': None,
                                   'responsable': vals.responsable.id,
                                   'etapa': vals.etapa,
                                   'categoria_documento': vals.categoria_documento.id,
                               }
                               ]]}
                tt = self.env['control.expediente_contrato'].browse(self.id)
                xd = tt.write(datos)

    @api.multi
    def borrar_expedientes(self):
        self.tabla_control.unlink()

    # METODO PARA CREAR NUEVO DOCUMENTO CON BOTON
    @api.multi
    def expediente_crear(self):
        # VISTA OBJETIVO
        view = self.env.ref('control_expediente.form_agregar_control_expediente')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Control Expediente',
            'res_model': 'control.expediente',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_auxiliar': True, 'default_auxiliar_comprimido': True},
            'view_id': view.id,
        }