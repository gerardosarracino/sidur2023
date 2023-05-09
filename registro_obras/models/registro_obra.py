from odoo import models, fields, api, exceptions
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class ejercicio(models.Model):
	_name = "registro.ejercicio"

	name = fields.Integer(string="Ejercicio", )


class unidadAdminSol(models.Model):
	_name = "registro.unidadadminsol"

	name = fields.Char(string="Descripción", )


class tipoProyecto(models.Model):
	_name = "registro.tipoproyecto"

	name = fields.Char(string="Tipo de proyecto", )


class tipoObraEtapa(models.Model):
	_name = "registro.tipoobraetapa"

	name = fields.Char(string="Tipo de proyecto", )


class tipoLocalidad(models.Model):
	_name = "registro.tipolocalidad"

	name = fields.Char(string="Tipo localidad", )


class unidadMedida(models.Model):
	_name = "registro.unidadm"

	name = fields.Char(string="Unidad medida", )


class registro_obra(models.Model):
	_name = "registro.obra"
	_rec_name = 'numero_obra'
	# _inherit = 'res.partner'

	id_sideop = fields.Integer('ID SIDEOP')

	name = fields.Char('ID SIDEOP', compute="id_sideop_metod")

	@api.one
	def id_sideop_metod(self):
		self.name = str(self.id_sideop)

	# MAP DRAW
	'''shape_name = fields.Char(string='Shape Name')
	shape_area = fields.Float(string='Area')
	shape_radius = fields.Float(string='Radius')
	shape_description = fields.Text(string='Description')
	shape_type = fields.Selection([
		('circle', 'Circle'), ('polygon', 'Polygon'),
		('rectangle', 'Rectangle')], string='Type', default='polygon',
		)
	shape_paths = fields.Text(string='Paths')'''

	numero_obra = fields.Char(string="Número de obra", placeholder='Numero de obra')

	ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", required=True )
	grupoObra = fields.Boolean(string="Grupo de obra")
	origen = fields.Many2one('generales.origenes_obra', 'origen', required=True )
	monto = fields.Float(string="Monto", )
	descripcion = fields.Text(string="Descripción", required=True )
	problematica = fields.Text(string="Problemática")
	unidadadminsol = fields.Many2one('registro.unidadadminsol', string="Unidad administrativa solicitante",
									 required=True )
	tipoObra = fields.Many2one('generales.tipo_obra', 'tipo_obra', required=True )
	tipoproyecto = fields.Many2one("registro.tipoproyecto", string="Tipo de proyecto",required=True  )
	tipoobraetapa = fields.Many2one("registro.tipoobraetapa", string="Tipo de obra etapa", required=True )
	estado = fields.Many2one('generales.estado', 'estado', required=True )

	municipio = fields.Many2one('generales.municipios', 'municipio delegacion')

	ubicacion = fields.Text(string="Ubicación")
	localidad = fields.Text(string="Localidad")
	cabeceraMunicipal = fields.Boolean(string="Cabecera municipal")
	tipolocalidad = fields.Many2one("registro.tipolocalidad", string="Tipo localidad", )
	# latitud = fields.Char(string="Latitud")
	# longitud = fields.Char(string="Longitud")

	partner_latitude = fields.Char(string='Geo Latitude', digits=(16, 5))
	partner_longitude = fields.Char(string='Geo Longitude', digits=(16, 5))

	beneficiados = fields.Char(string="Beneficiados", )
	metaFisicaProyecto = fields.Char(string="Meta física Proyecto", )
	# metaProyectoUnidad = fields.Many2one("registro.unidadm" ,string="Meta Proyecto Unidad", )
	metaProyectoUnidad = fields.Char(string="Meta Proyecto Unidad", )
	metaEjercicio = fields.Char(string="Meta ejercicio", )
	# metaEjercicioUnidad = fields.Many2one("registro.unidadm", string="Meta ejercicio unidad", )
	metaEjercicioUnidad = fields.Char(string="Meta ejercicio unidad", )
	justificacionTecnica = fields.Text(string="Justificación técnica", )
	justificacionSocial = fields.Text(string="Justificación social", )

	proyecto_ejecutivo = fields.Integer(compute='contar')
	seguimientoc = fields.Integer(compute='contar1')

	programada = fields.Integer(related="programada_sideop") # compute='contar2'

	programada_sideop = fields.Integer('programada')

	estate = fields.Selection([('planeada', 'Planeada'),('programada', 'Programada'),], default='planeada')

	estado_obra = fields.Char(compute="contar_programada")

	estatus_obra = fields.Selection([('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
								default='borrador')
	@api.one
	def borrador_progressbar(self):
		self.write({'estatus_obra': 'borrador', })

	@api.one
	def confirmado_progressbar(self):
		self.write({'estatus_obra': 'confirmado'})

	@api.one
	def validado_progressbar(self):
		self.write({'estatus_obra': 'validado'})

	@api.multi
	def _compute_commercial_partner(self):
		return "hola"

	@api.multi
	def decode_shape_paths(self):
		self.ensure_one()
		return safe_eval(self.shape_paths)

	@api.one
	def contar_programada(self):
		count = self.env['registro.programarobra'].search_count([('obra_planeada', '=', self.id),('estate2','!=','cancelado')])
		# count = self.programada_sideop
		count2 = self.env['registro.programarobra'].search_count([('obra_planeada', '=', self.id),('estate2','=','cancelado')])
		# count2 = self.programada_sideop

		if count == 0 and count2 == 0:
			self.estado_obra = 'Planeada'
		elif count > 0 and count2 ==0:
			self.estado_obra = 'Programada'
		elif count > 0 and count2 > 0:
			self.estado_obra = 'Programada'
		elif count == 0 and count2 > 0:
			self.estado_obra = 'Planeada'

	@api.one
	def contar(self):
		count = self.env['registro.proyectoejecutivo'].search_count([('name', '=', self.id)])
		self.proyecto_ejecutivo = count

	@api.one
	def contar1(self):
		count = self.env['registro.seguimientoobra'].search_count([('name', '=', self.id)])
		self.seguimientoc = count

	@api.one
	def contar2(self):
		count = self.env['registro.programarobra'].search_count([('name', '=', self.id),('estate2','!=','cancelado')])
		self.programada = count

#	@api.multi
#	def proyectoEjecutivo(self):
#		context = {
#		'default_name': self.id
#		}
#		return {
#		'type': 'ir.actions.act_window',
#		'name': 'Proyecto ejecutivo',
#		'res_model': 'registro.proyectoejecutivo',
#		'view_mode': 'tree,form',
#		'context': context,
#		'target': 'new',
#		}


class ProyectoEjecutivo(models.TransientModel):
	_name = 'registro.proyectoejecutivo'

	name1 = fields.Many2one('generales.apartados_proyectos', )
	name = fields.Many2one('registro.obra', readonly=True)
	documento = fields.Binary(string="Documento", )
	nombre = fields.Char(string="Nombre", )
	observaciones = fields.Text(string="Observaciones", )


class SeguimientoObra(models.TransientModel):
	_name = 'registro.seguimientoobra'

	name = fields.Many2one('registro.obra', readonly=True)
	seguimiento = fields.Html(string="Seguimiento", )


class ProgramarObra(models.Model):
	_name = 'registro.programarobra'
	_rec_name = 'descripcion'

	obra_adj_lic = fields.Boolean() # CUANDO SE ADJUDICA O SE FALLA

	Id_obraprogramada = fields.Integer('IDE OBRAPROGRAMADA')

	obra_planeada = fields.Many2one('registro.obra')

	programaInversion = fields.Many2one('generales.programas_inversion', required=True)

	@api.onchange('programaInversion')
	def cambiar_programada(self):
		b_obra = self.env['registro.obra'].browse(self.obra_planeada.id)
		# CREAR EVENTO
		datos = {'estate': 'programada'}
		lista = b_obra.write(datos)

	contrato_relacionado = fields.Char(string="Contratada", compute="contrato")

	@api.one
	def contrato(self):
		b_contrato = self.env['partidas.partidas'].search(
			[('obra.id', '=', self.id)])
		self.contrato_relacionado = b_contrato.nombre_partida

	categoriaProgramatica = fields.Many2one('generales.modalidades', required=True )

	fechaProbInicio = fields.Date(string="Fecha probable de inicio", required=True)
	fechaProbTermino = fields.Date(string="Fecha Probable de termino", required=True)

	@api.constrains('fechaProbInicio', 'fechaProbTermino' )
	def fechas_constrain(self):
		if self.fechaProbInicio > self.fechaProbTermino:
			raise ValidationError("La fecha de inicio no puede ser mayor a la de termino")
		elif self.fechaProbTermino < self.fechaProbInicio:
			raise ValidationError("La fecha de termino no puede ser menor a la de inicio")

	descripTotalObra = fields.Text(string="Descripción de la totalidad de la obra")
	conceptoEjecutar = fields.Text(string="Conceptos a ejecutar")
	select = [('1', 'Contrato'), ('2', 'Administracion directa'), ('3', 'Mixta')]
	modalidadEjecucion = fields.Selection(select, string="Modalidad de la ejecución", default="1", )
	avanceFisicoActual = fields.Float(string="Avance físico actual")
	avanceProgCierreEjerci = fields.Float(string="Avance programado al cierre del ejercicio")
	imagen1 = fields.Binary(string="Imagen uno")
	imagen2 = fields.Binary(string="Imagen dos")
	imagen3 = fields.Binary(string="Imagen tres")
	imagen4 = fields.Binary(string="Imagen cuatro")
	estate2 = fields.Selection([('activo', 'Activo'),('cancelado', 'Cancelado'),], default='activo')
	tipo = fields.Char(related="obra_planeada.tipoObra.tipo_obra")

	descripcion = fields.Text(related="obra_planeada.descripcion")

	estado = fields.Char(related="obra_planeada.estado.estado")
	municipio = fields.Char(related="obra_planeada.municipio.municipio_delegacion")
	ubicacion = fields.Text(related="obra_planeada.ubicacion")
	monto = fields.Float(related="obra_planeada.monto")
	estruc_finan = fields.Integer(compute='contar3')

	# BUSCAR SI LA OBRA ESTA ADJUDICADA
	'''adjudicacion_cont = fields.Integer(compute="adjudicacion_contar")
	licitacion_cont = fields.Integer(compute="licitacion_contar")
	contrato_cont = fields.Integer(compute="contrato_contar")
	# INICA METODOS PARA CONTAR ADJUDICADA, LICITADA O CONTRATADA
	@api.one
	def adjudicacion_contar(self):
		count = self.env['partidas.adjudicacion'].search_count([('obra', '=', self.descripcion)])
		self.adjudicacion_cont = count

	@api.one
	def licitacion_contar(self):
		count = self.env['partidas.licitacion'].search_count([('obra', '=', self.descripcion)])
		self.licitacion_cont = count

	@api.one
	def contrato_contar(self):
		count = self.env['partidas.partidas'].search_count([('obra', '=', self.descripcion)])
		self.contrato_cont = count'''

	# TERMINA METODOS PARA CONTAR ADJUDICADA, LICITADA O CONTRATADA

	@api.multi
	def borrador_progressbar_respuesta(self):
		for rec in self:
			rec.write({
				'estate2': 'cancelado',
				})

	@api.constrains('name')
	def contar2(self):
		count = self.env['registro.programarobra'].search_count([('name', '=', self.obra_planeada.id),('estate2','!=','cancelado')])
		if count>1:
			raise exceptions.ValidationError("La obra ya fue programada con anterioridad. Por favor verifique su información.")

	@api.one
	def contar3(self):
		count = self.env['registro.estructurafinanciera'].search_count([('obra_planeada', '=', self.id)])
		self.estruc_finan = count


class EstructuraFinanciera(models.Model):
	_name = "registro.estructurafinanciera"

	obra_planeada = fields.Many2one('registro.programarobra', readonly=True)
	descripcion = fields.Text(related="obra_planeada.descripcion")
	monto = fields.Float(related="obra_planeada.monto")
	iaoeFederal = fields.Float(string="Federal")
	iaoeEstatal = fields.Float(string="Estatal")
	iaoeMunicipal = fields.Float(string="Municipal")
	iaoeInstitucional = fields.Float(string="Institucional")
	iaoeOtros = fields.Float(string="Otros")
	sumaIaoe = fields.Float(string="Total", compute="_sumaiaoe", store=True)
	ideFederal = fields.Float(string="Federal")
	ideEstatal = fields.Float(string="Estatal")
	ideMunicipal = fields.Float(string="Municipal")
	ideInstitucional = fields.Float(string="Institucional")
	ideOtros = fields.Float(string="Otros")
	sumaIde = fields.Float(string="Total", compute="_sumaide", store=True)
	iarFederal = fields.Float(string="Federal")
	iarEstatal = fields.Float(string="Estatal")
	iarMunicipal = fields.Float(string="Municipal")
	iarInstitucional = fields.Float(string="Institucional")
	iarOtros = fields.Float(string="Otros")
	sumaIar = fields.Float(string="Total", compute="_sumaiar", store=True)
	Total = fields.Float(compute="_total", store=True)

	@api.depends('iaoeFederal','iaoeEstatal','iaoeMunicipal','iaoeInstitucional','iaoeOtros')
	def _sumaiaoe(self):
		for r in self:
			r.sumaIaoe = r.iaoeFederal + r.iaoeEstatal + r.iaoeMunicipal + r.iaoeInstitucional + r.iaoeOtros

	@api.depends('ideFederal','ideEstatal','ideMunicipal','ideInstitucional','ideOtros')
	def _sumaide(self):
		for r in self:
			r.sumaIde = r.ideFederal + r.ideEstatal + r.ideMunicipal + r.ideInstitucional + r.ideOtros

	@api.depends('iarFederal','iarEstatal','iarMunicipal','iarInstitucional','iarOtros')
	def _sumaiar(self):
		for r in self:
			r.sumaIar = r.iarFederal + r.iarEstatal + r.iarMunicipal + r.iarInstitucional + r.iarOtros

	@api.depends('sumaIaoe','sumaIde','sumaIar')
	def _total(self):
		for r in self:
			r.Total = r.sumaIaoe + r.sumaIde + r.sumaIar


class GoogleMapsDrawingShapeMixin(models.AbstractModel):
	_name = 'google_maps.drawing.shape.mixin'
	_description = 'Google Maps Shape Mixin'
	_rec_name = 'shape_name'

	shape_name = fields.Char(string='Name')
	shape_area = fields.Float(string='Area')
	shape_radius = fields.Float(string='Radius')
	shape_description = fields.Text(string='Description')
	shape_type = fields.Selection([
		('circle', 'Circle'), ('polygon', 'Polygon'),
		('rectangle', 'Rectangle')], string='Type', default='polygon',
		)
	shape_paths = fields.Text(string='Paths')

	@api.multi
	def decode_shape_paths(self):
		self.ensure_one()
		return safe_eval(self.shape_paths)