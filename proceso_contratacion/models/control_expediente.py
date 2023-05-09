from odoo import models, fields, api, exceptions


class ControlExpediente(models.Model):
    _name = 'control.expediente'
    _rec_name = 'nombre_documento'

    revisado = fields.Boolean(string="Revisado",  )
    odoo_user_admin = fields.Many2one('res.users', string='Residente obra:', store=True)  # compute="user_admin"

    categoria_documento = fields.Many2one(comodel_name="categoria.expediente",
                                          string="Seleccione a que tipo de categoria del documento a comprimir", )

    # PARTIDA ENLACE
    p_id = fields.Many2one(comodel_name="partidas.partidas", string="Partida", required=False, store=True)
    # CONTRATO ENLACE
    contrato_id = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="Contrato", required=False, store=True)

    select_etapa = [('1', 'PREVIO AL PROCESO DE CONTRATACIÓN'), ('2', 'DURANTE EL PROCESO DE CONTRATACIÓN'),
                    ('3', 'DESPUÉS DEL PROCEDIMIENTO DE CONTRATACIÓN Y ANTES DE EJECUTAR LA OBRA'),
                    ('4', 'DURANTE LA EJECUCIÓN DE LA OBRA'), ('5', 'DESPUÉS DE LA EJECUCIÓN DE LA OBRA')]

    etapa = fields.Selection(select_etapa, string="Etapa:", store=True)

    responsable = fields.Many2one(comodel_name='res.users', string='Responsable:')

    nombre = fields.Many2one('control_expediente.control_expediente', string="Nombre:") # relacion del documento
    nombre_documento = fields.Char(string="Nombre:", ) # nombre del documento

    orden = fields.Integer(string="Orden", ) # ORDEN DEL DOCUMENTO POR DEFAULT
    numeracion = fields.Integer(string="Numeracion", store=True) # NUMERACION DEL DOCUMENTO EN LA LISTA PARA SU ORDEN
    documento = fields.Binary(string="",  )

    @api.onchange('nombre')
    def etapa_activador(self):
        self.etapa = self.nombre.etapa
        self.responsable = self.nombre.responsable

    @api.onchange('url')
    def existe_activador(self):
        if self.url:
            self.existe = True
            self.aplica = False
        else:
            self.existe = False
            self.aplica = True

    @api.multi
    @api.onchange('categoria_documento')
    def posicion_documentos(self):
        if not self.categoria_documento:
            pass
        else:
            self.etapa = '4'
            self.auxiliar = True
            self.auxiliar_documentos_categoria = True
            self.ejercicio = self.contrato_id.ejercicio
            self.tipo_obra = self.contrato_id.tipo_obra


            search_documentos = self.env['control.expediente'].search([('contrato_id.id', '=', self.contrato_id.id),
                                                                       ('categoria_documento.id', '=',
                                                                        self.categoria_documento.id),
                                                                       ('auxiliar', '=', True)])
            orden = 0
            if self.categoria_documento.categoria_documento == "Estimacion":  # ESTIMACION
                orden = 44
            elif self.categoria_documento.categoria_documento == "Convenio":  # convenio
                orden = 49
            elif self.categoria_documento.categoria_documento == "Fps":  # fps
                orden = 55
            elif self.categoria_documento.categoria_documento == "Escalatoria":  # escalatoria
                orden = 58
            print(orden, ' orden')
            search_numero = self.env['control.expediente'].search(
                [('contrato_id.id', '=', self.contrato_id.id), ('orden', '=', orden)])[0]

            print(search_numero.numeracion, search_numero.nombre_documento, ' xxxx ')
            if not search_documentos:
                # si no existe algun documento con una categoria, posicionarlo debajo del documento con orden 44
                self.numeracion = search_numero.numeracion + 1
                self.nombre_documento = self.categoria_documento.categoria_documento.upper() + " 1"
                print('numeracion', self.numeracion)
            else:
                acum_docs = 0
                for i in search_documentos:
                    acum_docs += 1
                    self.numeracion = i.numeracion + 1
                    self.nombre_documento = self.categoria_documento.categoria_documento.upper() + " " + str(acum_docs+1)
                    print('numeracion 2', self.numeracion, i.nombre_documento)

    auxiliar = fields.Boolean(string="",  store=True)

    @api.model
    def create(self, values):
        if values['categoria_documento'] == '1':
            pass
        else:
            print(values['numeracion'])
            search_x = self.env['control.expediente'].search([('contrato_id.id', '=', values['contrato_id']),
                                                              ('auxiliar_documentos_categoria2', '=', False),
                                                              ('numeracion', '>', int(values['numeracion'] - 1))],
                                                             order='numeracion asc')

            if values['auxiliar_documentos_categoria2']:
                pass
            else:
                acum_nuevo = 0
                for vals in search_x:
                    acum_nuevo += 1
                    numeracion = values['numeracion'] + acum_nuevo
                    browse = self.env['control.expediente'].browse(vals['id'])
                    browse.write({'numeracion': numeracion})
                    # recorrer la numeracion una posicion abajo del que se acaba de insertar

            res = super(ControlExpediente, self).create(values)

            if values['auxiliar']: # CONDICIONAL PARA AGREGAR EL REGISTRO A LA TABLA PRINCIPAL
                datos = {'tabla_control':[[4, res.id,{}]]}
                b_control_contrato = self.env['control.expediente_contrato'].search(
                    [('contrato_id', '=', values['contrato_id'])])
                tt = self.env['control.expediente_contrato'].browse(b_control_contrato.id)
                xd = tt.update(datos)

            if values['auxiliar_documentos_categoria']: # CONDICIONAL PARA AGREGAR EL REGISTRO A LA TABLA COMPRIMIDA
                b_expediente_cats = self.env['control_expediente.control_expediente'].search(
                    [('categoria_documento', '=', values['categoria_documento'])],
                    order='orden asc')
                numeracion_cat = 0
                for vals in b_expediente_cats:
                    numeracion_cat += 1
                    aplica = None
                    if vals['orden'] == 45 or vals['orden'] == 48:
                        aplica = False
                    print(int(numeracion_cat + values['numeracion']))

                    if values['auxiliar_documentos_categoria2']:
                        numeracion_final = 0
                    else:

                        numeracion_final = numeracion_cat + values['numeracion']

                    datos_categorias = {
                        'numeracion': numeracion_final,
                        'orden': vals['orden'],
                        'nombre': vals['id'],
                        'aplica': aplica,
                        'auxiliar_documentos_categoria': False,
                        'auxiliar_documentos_categoria2': True,
                        'auxiliar': False,
                        'nombre_documento': vals['nombre'],
                        'contrato_id': values['contrato_id'],
                        'p_id': values['p_id'],
                        'responsable': None,
                        'etapa': vals['etapa'],
                        'id_documento_categoria': res.id,
                        'odoo_user_admin': 2,
                        'categoria_documento': values['categoria_documento'],
                    }
                    expe = self.env['control.expediente']
                    r = expe.create(datos_categorias)
            else:
                pass
            return res

    referencia = fields.Char(string="Referencia", required=False, )

    fecha = fields.Date(string="Fecha", required=False, )

    aplica = fields.Boolean(string="No Aplica",  )
    existe = fields.Boolean(string="Existe",  )

    comentarios = fields.Text(string="Comentarios", required=False, )

    # METODO PARA INGRESAR A RECURSOS BOTON
    @api.multi
    def vista_expediente(self):
        # VISTA OBJETIVO
        view = self.env.ref('control_expediente.form_control_expediente')
        # CONTADOR SI YA FUE CREADO
        count = self.env['control.expediente'].search_count([('id', '=', self.id)])
        # BUSCAR VISTA
        search = self.env['control.expediente'].search([('id', '=', self.id)])
        # SI YA FUE CREADA LA VISTA, ABRIR LA VISTA YA CREADA
        if count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Control Expediente',
                'res_model': 'control.expediente',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
                'res_id': search[0].id,
            }
        # NO A SIDO CREADA LA VISTA, CREARLA
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Control Expediente',
                'res_model': 'control.expediente',
                'view_mode': 'form',
                'target': 'new',
                'view_id': view.id,
            }

    tabla_control = fields.One2many('control.expediente', 'id_documento_categoria', ) # tabla de documentos comprimidos para categorias
    id_documento_categoria = fields.Many2one('control.expediente',) # tabla de documentos comprimidos para categorias

    auxiliar_documentos_categoria = fields.Boolean(store=True) # ESTE CAMPO ES UN AUXILIAR QUE INDICA QUE ES UN DOCUMENTO ...
    auxiliar_documentos_categoria2 = fields.Boolean(store=True) # ESTE CAMPO ES UN AUXILIAR QUE INDICA QUE ES UN DOCUMENTO ...
    # AGREGADO A MANO DE CATEGORIA, EJEMPLO DOCUMENTOS DE ESTIMACIONES O CONVENIOS

    url = fields.Char('URL de descarga')

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="contrato_id.ejercicio")
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra", related="contrato_id.tipo_obra")
    obra = fields.Many2one('registro.programarobra', related="p_id.obra")

    @api.multi
    def cargar_documento(self):
        original_url = "http://sidur.galartec.com:9001/documentos.php?id=" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    @api.multi
    def descargar_documento(self):
        original_url = "http://sidur.galartec.com:9001" + str(self.url)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    @api.multi
    def eliminar_documento(self):
        original_url = "http://sidur.galartec.com:9001/eliminar.php?id=" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    @api.multi
    def agregar_expedientes(self): # actualiza la lista con los expedientes
        b_contrato = self.env['proceso.elaboracion_contrato'].search([('id', '=', self.contrato_id.id)])[0]

        b_expediente = self.env['control_expediente.control_expediente'].search(
            [('categoria_documento.id', '=', self.categoria_documento.id)])

        for vals in b_expediente:
            datos = {'tabla_control':
                         [[0, 0,
                           {
                               'orden': vals.orden,
                               'nombre': vals.id,
                               'nombre_documento': vals.nombre,
                               'categoria_documento': vals.categoria_documento.id,
                               'contrato_id': b_contrato.id,
                               'responsable': vals.responsable.id,
                               'etapa': vals.etapa,
                           }
                           ]]}
            tt = self.env['control.expediente'].browse(self.id)
            xd = tt.write(datos)

    contratista = fields.Many2one('contratista.contratista', related="contrato_id.contratista")
    total_siva = fields.Float(string="Monto Total Contratado cIva:", digits=(12, 2),
                              related="p_id.total")  # total con iva
    residente_obra = fields.Many2many('res.users', 'name', string='Residente obra:', related="p_id.residente_obra")
    residente_obra_2 = fields.Many2one('res.users', string='Residente obra:')

    # importacion sideop
    id_sideop = fields.Integer()
    id_expediente = fields.Integer()


class ReporteExpedientes(models.Model):
    _name = 'expediente.memorandum'
    _rec_name = 'id_reporte'

    fecha_memo = fields.Date(string="", required=False, )
    id_reporte = fields.Char(store=True, string="No. de Memorándum")
    tabla_reporte = fields.Many2many('expediente.tabla_reporte')
    comentarios = fields.Text('Comentarios Generales')

    @api.multi
    def imprimir_memorandum_excel(self):
        url = "/memorandum/memorandum/?id=" + str(self.id)
        return {"type": "ir.actions.act_url", "url": url, "target": "new", }

    @api.model
    def create(self, values):
        count2 = self.env['expediente.memorandum'].search_count([])
        x = count2 + 1
        values['id_reporte'] = "{:04d}".format(x)
        return super(ReporteExpedientes, self).create(values)


class ReporteTabla(models.Model):
    _name = 'expediente.tabla_reporte'
    _rec_name = 'contrato_id'

    id_numeracion = fields.Integer(string="ID", )  # ORDEN DEL DOCUMENTO POR DEFAULT
    contrato_id = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="No. de Contrato", store=True)
    memorandum_id = fields.Many2one(comodel_name="expediente.memorandum", string="ID memorandum", store=True)
    p_id = fields.Many2one(comodel_name="partidas.partidas", string="No. de Partida", store=True)
    nombre_documento = fields.Many2one('control.expediente', string="Documento")  # nombre del documento
    observaciones = fields.Text(string="Observaciones", required=False, )

    @api.multi
    def borrar(self):
        self.env['expediente.tabla_reporte'].search([('id', '=', self.id)]).unlink()

    @api.model
    def create(self, values):
        search = self.env['expediente.tabla_reporte'].search([('memorandum_id', '=', values['memorandum_id'])])
        acum_nuevo = 0
        for vals in search:
            acum_nuevo += 1
            numeracion = acum_nuevo
            browse = self.env['expediente.tabla_reporte'].browse(vals['id'])
            browse.write({'id_numeracion': numeracion})
        values['id_numeracion'] = acum_nuevo + 1
        return super(ReporteTabla, self).create(values)



class LibrosBlancos(models.Model):
    _name = 'expediente.libros_blancos'
    _rec_name = 'nombre_documento_m2o'
    # _inherit = "mail.thread"
    
    numero_documento = fields.Integer('No.')
    nombre_documento = fields.Char(string="", required=False, )
    nombre_documento_m2o = fields.Many2one('expediente.documentos_revision', string="", required=False, )

    select_sevi = [('1', 'Si'), ('2', 'No')]
    sevi = fields.Selection(select_sevi, string="Sevi", related="nombre_documento_m2o.sevi") 
    nombre_sevi = fields.Char('Nombre Sevi', related="nombre_documento_m2o.nombre_sevi")

    select_etapa = [('1', 'PREVIO A LA EJECUCIÓN'), ('2', 'DURANTE LA EJECUCIÓN'),
                    ('3', 'DESPUÉS DE LA EJECUCIÓN')]
    etapa = fields.Selection(select_etapa, string="Etapa", required=True)
    
    select_aplica = [('Si', 'Si'), ('No', 'No'), ('Por definir', 'Por definir')]
    select_existe = [('N/A', 'N/A'), ('No', 'No'), ('Si', 'Si'), ('Por definir', 'Por definir')]
    aplica = fields.Selection(select_aplica, string="Aplica")
    existe = fields.Selection(select_existe, string="Existe")
    Observaciones = fields.Text(string="Observaciones", required=False, )
    p_id = fields.Many2one(comodel_name="partidas.partidas", string="ENLACE A PARTIDAS", required=False, store=True)
    contrato_id = fields.Many2one(comodel_name="proceso.elaboracion_contrato", string="ENLACE A CONTRATOS", required=False, store=True)
    libros_blancos_id = fields.Many2one(comodel_name="libros.blancos", string="ENLACE A LIBROS B.", required=False, store=True)
    entregado = fields.Boolean(string='Entregado')
    responsable_revision_exp = fields.Many2one('res.users', string='Responsable')   
    fecha_entregado = fields.Date(string="Fecha de Entregado", )

    # RELATED
    estado_obra_m2o = fields.Many2one('semaforo.estado_obra_lista', string="Estado", store=True) 
    unidadadminsol = fields.Many2one('registro.unidadadminsol', string="Unidad administrativa solicitante",  )
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", )
    contratista = fields.Many2one('contratista.contratista', related="contrato_id.contratista")
    total_siva = fields.Float(string="Monto Total Contratado cIva:", digits=(12,2), related="p_id.total") # total con iva
    residente_obra = fields.Many2many('res.users', 'name', string='Residente obra:', related="p_id.residente_obra")
    residente_obra_2 = fields.Many2one('res.users', string='Residente obra:')
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra", )
    obra = fields.Many2one('registro.programarobra', related="p_id.obra")
    programa_inversion = fields.Many2one('generales.programas_inversion', string="Programa de Inversion")

    verificado_expediente = fields.Boolean('Verificado', related="libros_blancos_id.verificado_expediente")
    reviso_expediente = fields.Boolean(string='Revisado', related="libros_blancos_id.reviso_expediente")
    fecha_revisado_exp = fields.Date(string="Fecha de Revisado", required=False, related="libros_blancos_id.fecha_revisado_exp")
    fecha_verificado_exp = fields.Date(string="Fecha de Verificado", required=False, related="libros_blancos_id.fecha_verificado_exp")


class DocumentosRevision(models.Model):
    _name = 'expediente.documentos_revision'
    _rec_name = 'nombre_documento'

    select_etapa = [('1', 'PREVIO A LA EJECUCIÓN'), ('2', 'DURANTE LA EJECUCIÓN'),
                    ('3', 'DESPUÉS DE LA EJECUCIÓN')]
    etapa = fields.Selection(select_etapa, string="Etapa", required=True)
    nombre_documento = fields.Char(string="Nombre", required=True)
    numero_documento = fields.Char(string="Orden", required=True)
    unidadadminsol = fields.Many2one('registro.unidadadminsol', string="Unidad administrativa solicitante",required=True )

    select_relevancia = [('1', 'Alta'), ('2', 'Media'),
                    ('3', 'Baja')]
    relevancia = fields.Selection(select_relevancia, string="Relevancia")

    select_sevi = [('1', 'Si'), ('2', 'No')]
    sevi = fields.Selection(select_sevi, string="Sevi")
    nombre_sevi = fields.Char('Nombre Sevi')


class EntregaDocumentos(models.Model):
    _name = 'lb.entrega_documentos'
    _rec_name = 'id_entrega'

    id_entrega = fields.Char()

    p_id = fields.Many2one(comodel_name="partidas.partidas", string="ENLACE A PARTIDAS", required=False, store=True)

    @api.multi
    @api.onchange('contrato', 'entrega_doc_checklist')
    def datos_partida(self):
        partida = self.env['partidas.partidas'].search([('numero_contrato.id', '=', self.contrato.id)])[0]
        for i in partida:
            print(i.nombre_contrato)
            self.p_id = i.id

    contrato = fields.Many2one('proceso.elaboracion_contrato', string='ENLACE A CONTRATOS', store=True)
    libros_blancos_id = fields.Many2one(comodel_name="libros.blancos", string="ENLACE A LIBROS B.", required=False, store=True)

    nombre_registro = fields.Char(string="Nombre de Registro")

    fecha = fields.Date(string="Fecha", required=False, default=fields.Date.today())
    comentarios_generales = fields.Text(string="Comentarios Generales", required=False, )

    
    @api.model
    def create(self, values):
        count = self.env['lb.entrega_documentos'].search_count([('contrato.id', '=', values['contrato'])])
        count2 = self.env['lb.entrega_documentos'].search_count([])

        x = 1000 + count2 + 1
        registro = 'ENTREGA No. ' + str(x)
        values['nombre_registro'] = str(registro)
        values['id_entrega'] = str(x)
        return super(EntregaDocumentos, self).create(values)

    entrega_doc_checklist = fields.Many2many('lb.entregas_checklist', string='Documentos Checklist', store=True)

    @api.multi
    def unlink(self):
        self.entrega_doc_checklist.unlink()
        return super(EntregaDocumentos, self).unlink()


class EntregaDocumentosChecklists(models.Model):
    _name = 'lb.entregas_checklist'
    _rec_name = 'documento'

    entrega_id = fields.Many2one('lb.entrega_documentos', string="ID entrega")

    documento = fields.Many2one('expediente.documentos_revision', required=True)
    unidadadminsol = fields.Many2one('registro.unidadadminsol', string="Unidad administrativa solicitante", related="documento.unidadadminsol" )

    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Contrato', store=True)

    comentario = fields.Text(string="Comentario")

    nombre_documento = fields.Char(string="Nombre del Documento", required=False, related="documento.nombre_documento")
    numero_documento = fields.Char(string="Orden", related="documento.numero_documento")
    # select_aplica = [('Si', 'Si'), ('No', 'No'), ('Por definir', 'Por definir')]
    # select_existe = [('N/A', 'N/A'), ('No', 'No'), ('Si', 'Si'), ('Por definir', 'Por definir')]

    # Observaciones = fields.Text(string="Observaciones", )
    
    # entrega_doc_enlace = fields.Many2one(comodel_name="lb.entrega_documentos", string="ENLACE A ENTREGA DOCS", store=True)

    select_etapa = [('1', 'PREVIO A LA EJECUCIÓN'), ('2', 'DURANTE LA EJECUCIÓN'),
                    ('3', 'DESPUÉS DE LA EJECUCIÓN')]
    etapa = fields.Selection(select_etapa, string="Etapa", related="documento.etapa")

    # ---
    # documento = fields.Many2one('expediente.documentos_revision', required=True)
    # p_id = fields.Many2one(comodel_name="partidas.partidas", string="ENLACE A PARTIDAS", store=True)
    # libros_blancos_id = fields.Many2one(comodel_name="libros.blancos", string="ENLACE A LIBROS B.", required=False, store=True)


class LibrosBlancosx(models.Model):
    _name = 'libros.blancos'
    _rec_name = 'contrato'

    contrato = fields.Many2one('proceso.elaboracion_contrato', string='Contrato', store=True)

    # ELEMENTOS PARA LA VISTA INFORMATIVOS
    nombre_obra = fields.Text(string="Obra", related="contrato.name")
    contratista = fields.Many2one('contratista.contratista', related="contrato.contratista")
    radio_adj_lic = [('1', "Licitación"), ('2', "Adjudicación")]
    tipo_contrato = fields.Selection(radio_adj_lic, string="Tipo de Contrato", store=True, related="contrato.tipo_contrato")

    estado_obra_m2o = fields.Many2one('semaforo.estado_obra_lista', string="Estado", store=True) 

    tabla_libros_blancos = fields.Many2many('expediente.libros_blancos', string='Revision de Expedientes', store=True)
    porcentaje_existencia = fields.Float(string="% Existencia", store=True)
    num_faltantes = fields.Integer(string="# Faltantes", store=True)



    @api.multi
    @api.onchange('tabla_libros_blancos')
    def onchange_method(self):
        if not self.tabla_libros_blancos:
            pass
        else:
            count_existencia = 0
            count_aplica = 0
            c_faltantes = 0
            for i in self.tabla_libros_blancos:
                if i.existe == 'Si':
                    count_existencia += 1
                if i.aplica == 'Si':
                    count_aplica += 1
                if i.aplica == 'Si' and i.existe != 'Si':
                    c_faltantes += 1
            if count_aplica == 0 or count_existencia == 0:
                pass
            else:
                self.porcentaje_existencia = (count_existencia / count_aplica) * 100
                self.num_faltantes = c_faltantes

    registrado = fields.Boolean('Registrado')
    reviso_expediente = fields.Boolean('Revisado')
    verificado_expediente = fields.Boolean('Verificado')
    fecha_revisado_exp = fields.Date(string="Fecha de Revisado", required=False, )
    fecha_verificado_exp = fields.Date(string="Fecha de Verificado", required=False, )
    comentarios_expediente = fields.Text(string="Comentario", required=False, )
    responsable_revision_exp = fields.Many2one('res.users', string='Responsable')  # compute="user_admin"
    responsable_ficha = fields.Many2one('res.users', string='Ficha Responsable', compute="ficha_respo")  # compute="user_admin"

    digitalizado = fields.Boolean('Digitalizado')
    fecha_digitalizado = fields.Date(string="Fecha de Digitalizado", required=False, )
    responsable_digitalizado = fields.Many2one('res.users', string='Digitalizado Responsable')
    numero_tomos = fields.Integer(string='Numero de Tomos')

    @api.one
    def ficha_respo(self):
        context = self._context
        current_uid = context.get('uid')
        self.responsable_ficha = self.env['res.users'].browse(current_uid)

    p_id = fields.Many2one(comodel_name="partidas.partidas", string="ENLACE A PARTIDAS", store=True) # compute="datos_partida"

    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", related="contrato.ejercicio")
    tipo_obra = fields.Many2one('generales.tipo_obra', string="Tipo de Obra", related="contrato.tipo_obra")

    programaInversion = fields.Many2one('generales.programas_inversion', string="Programa de Inversión", related="p_id.programaInversion")
    contratista = fields.Many2one('contratista.contratista', related="p_id.contratista")
    municipio = fields.Many2one('generales.municipios', 'Municipio', related="p_id.municipio")
    localidad = fields.Text(string="Localidad", readonly="True", related="p_id.obra.obra_planeada.localidad")
    fecha_anticipos = fields.Date(string="Fecha Anticipo", related="p_id.fecha_anticipos")
    total_anticipo = fields.Float(string="Total Anticipo", related="p_id.total_anticipo", digits=(12, 2))
    a_fis = fields.Float(string="", related="p_id.a_fis", digits=(12, 2) )
    porcentajeProgramado = fields.Float(string="", digits=(12, 2), related="p_id.porcentajeProgramado") 
    total = fields.Float(string="Monto Total Contratado:", digits=(12,2), related="p_id.total")
    supervisionexterna1 = fields.Many2one('proceso.elaboracion_contrato', string="Supervisión externa:", related="p_id.numero_contrato.supervisionexterna1")
    fecha = fields.Date(string="Fecha", related="p_id.numero_contrato.fecha")
    fechainicio = fields.Date(string="Fecha de Inicio", related="p_id.numero_contrato.fechainicio")
    fechatermino = fields.Date(string="Fecha de Termino", related="p_id.numero_contrato.fechatermino")
    director_obras = fields.Char('Director de obras:', related="p_id.director_obras")
    estado = fields.Many2one('generales.estado', 'Municipio', related="p_id.obra.obra_planeada.estado")
    fecha_termino_convenida = fields.Date('Fecha Termino Convenida', related="p_id.fecha_termino_convenida" )
    semaforo_tags = fields.Many2many(comodel_name="semaforo.categorias", string="Tags", related="p_id.semaforo_tags")
   

    '''@api.multi
    def datos_partida(self):
        partida = self.env['partidas.partidas'].search([('numero_contrato.id', '=', self.contrato.id)])
        for i in partida:
            self.p_id = i.id'''

    @api.multi
    def unlink(self):
        self.tabla_libros_blancos.unlink()
        return super(LibrosBlancosx, self).unlink()