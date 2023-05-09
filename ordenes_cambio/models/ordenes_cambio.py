from odoo import models, fields, api, exceptions
from datetime import datetime
import calendar
import datetime


class OrdenesCambio(models.Model):
    _name = 'ordenes.ordenes_cambio'
    _rec_name = 'id_partida'

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    numero_contrato = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Numero de Contrato", related="id_partida.numero_contrato")
    contratista = fields.Many2one('contratista.contratista', related="id_partida.contratista")
    obra = fields.Many2one('registro.programarobra', related="id_partida.obra")
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="id_partida.ejercicio")
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo", related="id_partida.obra.obra_planeada.tipoObra")

    # ordenes_conceptos_espejo = fields.Many2many('ordenes.conceptos_espejo', store=True)  # ORDENES DE CAMBIO CONCEPTOS EN ESPEJO
    ordenes_conceptos_espejo = fields.Many2many('proceso.conceptos_part', related="id_partida.conceptos_partidas")  # ORDENES DE CAMBIO CONCEPTOS EN ESPEJO
    ordenes_conceptos_related = fields.Many2many('ordenes.conceptos_espejo', related="id_partida.ordenes_conceptos")

    total_contratado = fields.Float('Total Contratado', related="id_partida.total")
    total_catalogo = fields.Float('Total Catalogo', related="id_partida.total_catalogo")
    diferencia = fields.Float('Diferencia', related="id_partida.diferencia")

    '''@api.multi
    @api.onchange('id_partida')
    def conceptos_espejo(self):
        b_conceptos = self.env['partidas.partidas'].search(
            [('id', '=', self.id_partida.id)])

        self.update({
            'ordenes_conceptos_espejo': [[5]]
        })

        for y in b_conceptos.conceptos_partidas:
            self.update({
                'ordenes_conceptos_espejo': [
                    [0, 0, {'id_partida': self.id_partida, 'categoria': y.categoria,
                            'related_categoria_padre': y.related_categoria_padre,
                            'clave_linea': y.clave_linea, 'concepto': y.concepto,
                            'medida': y.medida,
                            'importe': y.importe,
                            'precio_unitario': y.precio_unitario,
                            'cantidad': y.cantidad}]]
            })'''

    @api.multi
    def OrdenesLista(self):
        # VISTA OBJETIVO
        form = self.env.ref('ordenes_cambio.vista_form_ordenes_lista_cambio')
        tree = self.env.ref('ordenes_cambio.ordenes_cambio_lista_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ordenes de Cambio',
            'res_model': 'ordenes.lista_ordenes_cambio',
            'view_mode': 'tree,form',
            'target': 'current',
            'view_id': False,
            'domain': [('id_partida', '=', self.id_partida.id)],
            'views': [
                (tree.id, 'tree'),
                (form.id, 'form'),
            ],
        }

    '''@api.multi
    def unlink(self):
        self.ordenes_conceptos_espejo.unlink()
        return super(OrdenesCambio, self).unlink()'''


class ListaOrdenes(models.Model):
    _name = 'ordenes.lista_ordenes_cambio'
    _rec_name = 'numero_orden'

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    id_orden = fields.Many2one(comodel_name="ordenes.ordenes_cambio", string="id orden", store=True)
    ordenes_conceptos = fields.Many2many('ordenes.conceptos_lista', store=True)
    numero_orden = fields.Integer(store=True)
    comentario_orden = fields.Text('Comentario General de la Orden de Cambio')
    monto_orden = fields.Float('Monto de la Orden de Cambio', store=True)
    aplicado = fields.Boolean(string="Indica si ya fue Aplicado", store=True)

    @api.multi
    @api.onchange('ordenes_conceptos')
    def onchange_monto_orden(self):
        acum = 0
        for i in self.ordenes_conceptos:
            acum += i.importe
            self.monto_orden = acum

    @api.multi
    def AplicarCambios(self):
        datos = {}
        self.aplicado = True
        b_partida = self.env['partidas.partidas'].browse(self.id_partida.id)
        for conceptos in self.ordenes_conceptos:
            datos = ({
                'ordenes_conceptos': [[0, 0, {'id_partida': self.id_partida.id,
                   'categoria': conceptos.categoria.id,
                   'related_categoria_padre': conceptos.related_categoria_padre.id,
                   'clave_linea': conceptos.clave_linea,
                   'concepto': conceptos.concepto,
                   'medida': conceptos.medida,
                   'precio_unitario': conceptos.precio_unitario,
                   'importe': conceptos.importe,
                   'cantidad': conceptos.cantidad}]]
            })
            r = b_partida.write(datos)

    @api.multi
    def unlink(self):
        self.ordenes_conceptos.unlink()
        return super(ListaOrdenes, self).unlink()

    @api.model
    def create(self, values):
        search = self.env['ordenes.lista_ordenes_cambio'].search_count([('id_partida', '=', values['id_partida'])])
        values['numero_orden'] = int(search + 1)
        return super(ListaOrdenes, self).create(values)


class OrdenesConceptosLista(models.Model):
    _name = 'ordenes.conceptos_lista'
    _rec_name = 'clave_linea'

    concepto_partida = fields.Many2one(comodel_name="proceso.conceptos_part", string="Seleccionar Concepto", required=False, )

    @api.onchange('concepto_partida')
    def onchange_concepto(self):
        self.related_categoria_padre = self.concepto_partida.related_categoria_padre.id
        self.categoria = self.concepto_partida.categoria.id
        self.descripcion = self.concepto_partida.descripcion
        self.clave_linea = self.concepto_partida.clave_linea
        self.concepto = self.concepto_partida.concepto
        self.medida = self.concepto_partida.medida
        self.precio_unitario = self.concepto_partida.precio_unitario
        self.cantidad = self.concepto_partida.cantidad
        self.importe = self.concepto_partida.importe

    related_categoria_padre = fields.Many2one('catalogo.categoria', store=True)  # related="categoria.parent_id", store=True
    categoria = fields.Many2one('catalogo.categoria', 'Categoria', store=True)
    descripcion = fields.Text('Descripción',store=True)
    name = fields.Many2one('catalogo.categoria', 'Categoria Padre',store=True)
    clave_linea = fields.Char('Clave',store=True)
    concepto = fields.Text(store=True)
    medida = fields.Char(store=True)
    precio_unitario = fields.Float(store=True)
    cantidad = fields.Float(store=True)
    importe = fields.Float(compute="sumaCantidad", store=True)

    comentario = fields.Text(string="Comentario de Orden de Cambio", required=False, )

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", store=True)
    id_orden = fields.Many2one(comodel_name="ordenes.ordenes_cambio", string="id orden", store=True)

    @api.multi
    def borrar(self):
        self.unlink()
        return super(OrdenesConceptosLista, self).unlink()

    @api.multi
    @api.onchange('precio_unitario', 'cantidad')
    def sumaCantidad(self):
        for rec in self:
            rec.update({
                'importe': rec.cantidad * rec.precio_unitario
            })





