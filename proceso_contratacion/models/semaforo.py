from odoo import _, models, fields, api, exceptions, tools
from datetime import datetime, date


class EstadoObra(models.Model):
    _name = 'semaforo.estado_obra'

    partidaid = fields.Many2one('partidas.partidas')
    fecha = fields.Date(string="Fecha", required=True )
    descripcion = fields.Text(string="Decripción", required=True )

    select_estado = [('Terminado', 'Terminado'), ('En Ejecucion', 'En Ejecucion'), ('Sin Anticipo', 'Sin Anticipo'),
                          ('Terminado Anticipadamente', 'Terminado Anticipadamente'), ('Rescindido', 'Rescindido'), ('En Observacion', 'En Observacion'),
                     ('Nueva', 'Nueva'), ('Fuera de Semaforo', 'Fuera de Semaforo'), ('Falta Doc_cierre', 'Falta Doc_cierre'),
                     ('Suspendida', 'Suspendida')]
    tipo_estado = fields.Selection(select_estado, string="Estado", required=True)

    estado_obra = fields.Many2one('semaforo.estado_obra_lista', string="Estado")

    @api.multi
    def borrar(self):
        self.env['semaforo.estado_obra'].search([('id', '=', self.id)]).unlink()

    # METODO PARA ACTUALIZAR EL ESTADO EN EL SEMAFORO, BASANDOSE EN LA FECHA MAYOR
    @api.model
    def create(self, values):
        b_partida = self.env['partidas.partidas'].browse(values['partidaid'])
        lista = []
        max_value = None
        for i in b_partida.estado_obra:
            lista.append(str(i.fecha))
        if not values['fecha']:
            pass
        else:
            print(lista)
            if not lista:
                datos = {'estado_obra_m2o': values['estado_obra']}
                x = b_partida.write(datos)
            else:
                f = datetime.strptime(str(max(lista)), "%Y-%m-%d")
                fecha_estado = datetime.strptime(str(values['fecha']), "%Y-%m-%d")
                ff = datetime(fecha_estado.year, fecha_estado.month, fecha_estado.day)
                ff2 = datetime(f.year, f.month, f.day)
                if ff < ff2:
                    # print(' LA FECHA ACTUAL ES MENOR A LAS DE LA TABLA, NO ACTUALIZAR ESTADO')
                    b_estados = self.env['semaforo.estado_obra'].search([('partidaid.id', '=', values['partidaid'])])
                    for x in b_estados:
                        if str(x.fecha) == str(max(lista)):
                            datos = {'estado_obra_m2o': x.estado_obra.id}
                            xx = b_partida.write(datos)
                        else:
                            pass
                else:
                    # print(' LA FEHCA ACTUAL ES MAYOR, ACTUALIZAR ESTADO')
                    datos = {'estado_obra_m2o': values['estado_obra']}
                    x = b_partida.write(datos)
        return super(EstadoObra, self).create(values)


class Actividad(models.Model):
    _name = 'semaforo.actividad'

    partidaid = fields.Many2one('partidas.partidas')
    titulo = fields.Char(string="Título", required=True)
    contenido = fields.Text(string="Decripción", required=True)

    fecha = fields.Date(string="Fecha de vencimiento", required=True )

    select_estado = [('Abierto', 'Abierto'), ('Cerrado', 'Cerrado'), ('Cancelado', 'Cancelado')]
    tipo_estado = fields.Selection(select_estado, string="Estado", required=True)

    @api.multi
    @api.onchange('tipo_estado')
    def _mandar_estadox(self):
        b_partida = self.env['partidas.partidas'].browse(self.partidaid.id)
        datos = {'tipo_estado_actividad': self.tipo_estado}
        x = b_partida.write(datos)


class InformeEjecutivo(models.Model):
    _name = 'semaforo.informe'
    _rec_name = "nombre_informe"

    nombre_informe = fields.Char('Nombre Informe')

    descripcion_informe = fields.Text("Descripcion del Informe", required=True)
    fecha_informe = fields.Date("Fecha del Informe", required=True)

    fecha_inicio = fields.Date(string="Fecha Inicio del Informe", required=True, )
    fecha_termino = fields.Date(string="Fecha Termino del Informe", required=True, )

    partidasm2m = fields.Many2many('partidas.partidas', string='BUSQUEDA')

    ejercicio = fields.Many2many("registro.ejercicio", string="Ejercicio")
    contratos = fields.Many2many("semaforo.contratos", string="Tabla de Contratos en Ejecucion", ondelete='restrict')

    informe_completo = fields.Boolean(store=True)

    @api.multi
    @api.onchange('contratos')
    def verificar_completo(self):
        acum = 1
        acum2 = 1
        for i in self.contratos:
            acum2 += 1
            if i.Completo:
                acum += 1
            else:
                pass
        if acum == acum2:
            self.informe_completo = True


    @api.multi
    def accion_informe(self):
        original_url = "http://sidur.galartec.com:4000/informe/" + str(self.id)
        return {
            "type": "ir.actions.act_url",
            "url": original_url,
            "target": "new",
        }

    '''@api.multi
    def unlink(self):
        visit_obj = self.env['semaforo.contratos']
        obj = visit_obj.search([('id_informe', '=', self.id)])
        if obj:
            raise exceptions.ValidationError(_("You are trying to delete a record that is still referenced!"))
        return super(InformeEjecutivo, self).unlink()'''

    @api.multi
    def AplicarFiltro(self):
        self.nombre_informe = 'Informe ' + str(self.id)
        for partidas in self.partidasm2m:
            b_existencias = self.env['semaforo.contratos'].search([('id_informe', '=', self.id),
                                                                   ('id_partida.id', '=', partidas.id)])
            if b_existencias:
                pass
            else:
                informe_general = ''
                informe_avance = ''
                fecha_avance = ''
                comentario = ''
                for y in partidas.avance_semaforo:
                    informe_avance = y.com_avance_obra
                    informe_general = y.comentarios_generales
                    fecha_avance = y.fecha_actual

                informe = str(informe_avance) + "\n" + str(informe_general)

                for o in partidas.comentario_obra:
                    comentario = o.comentario

                self.update({
                    'contratos': [[0, 0, {
                        'id_informe': self.id,
                        'id_partida': partidas.id,
                        'nombre_partida': partidas.nombre_partida,
                        'a_fis': partidas.a_fis,
                        'a_fin': partidas.a_fin,
                        'atraso': partidas.atraso,
                        'color_semaforo': partidas.color_semaforo,
                        'porcentajeProgramado': partidas.porcentajeProgramado,
                        'comentario': comentario,
                        'ultimo_coment_avance': informe,
                        'fecha_informe': self.fecha_informe,
                        'fecha_avance': fecha_avance,
                        'tipo_estado_obra': partidas.tipo_estado_obra,
                        'ejercicio': partidas.ejercicio,
                    }]]
                })

            self.update({
                'partidasm2m': [[5]]
            })


class FotosInforme(models.Model):
    _name = 'semaforo.fotos_i'

    semaforo_contrato = fields.Many2one("semaforo.contratos", string="Partida Id", store=True)
    fotos =  fields.Binary(String="Agregar fotos")

    image_medium = fields.Binary(string="Imagen Reducida",
                                 store=True,
                                 compute="_get_image")

    @api.one
    @api.depends("fotos")
    def _get_image(self):
        image = self.fotos
        data = tools.image_get_resized_images(image)
        self.image_medium = data["image_medium"]
        return True


class InformeContratos(models.Model):
    _name = 'semaforo.contratos'
    _rec_name = 'id_informe'

    id_informe = fields.Char(store=True)
    fecha_informe = fields.Date()
    id_partida = fields.Many2one("partidas.partidas", string="Partida Id", store=True)
    nombre_partida = fields.Char('# Contrato', store=True)
    obra = fields.Many2one(string='Obra:', related="id_partida.obra")
    a_fis = fields.Float(string="Av.Fis", store=True, digits=(12, 2))
    a_fin = fields.Float(string="Av.Fin", store=True, digits=(12, 2))
    atraso = fields.Float(string="Atraso", store=True, digits=(12, 2))
    porcentajeProgramado = fields.Float(string="Av.Prog", store=True, digits=(12, 2))

    fecha_avance = fields.Date('Ultima Fecha del Avance')
    ultimo_coment_avance = fields.Text('Comentario de avance')

    select_estado = [('Terminado', 'Terminado'), ('En Ejecucion', 'En Ejecucion'), ('Sin Anticipo', 'Sin Anticipo'),
                     ('Terminado Anticipadamente', 'Terminado Anticipadamente'), ('Rescindido', 'Rescindido'),
                     ('En Observacion', 'En Observacion'),
                     ('Nueva', 'Nueva'), ('Fuera de Semaforo', 'Fuera de Semaforo'),
                     ('Falta Doc_cierre', 'Falta Doc_cierre'),
                     ('Suspendida', 'Suspendida')]

    tipo_estado_obra = fields.Selection(select_estado, string="Estado", store=True)
    ejercicio = fields.Many2one("registro.ejercicio", string="Ejercicio", store=True)
    comentario = fields.Text(string="Comentario")
    Completo = fields.Boolean(string="Completo")

    select_color = [('Verde', 'Verde'), ('Amarillo', 'Amarillo'), ('Rojo', 'Rojo')]
    color_semaforo = fields.Selection(select_color, string="Estado de Semaforo", store=True)
    fotos_informe = fields.Many2many('semaforo.fotos_i', string="Fotos para el informe")

    dias = fields.Integer(string="", compute="fecha_calculo" )

    contratista = fields.Many2one('contratista.contratista', string='Contratista', related="id_partida.contratista")

    localidad = fields.Text(string="Localidad", related="id_partida.localidad")

    programa_semaforo = fields.Many2many(comodel_name="proceso.programa", related="id_partida.programa_semaforo", string="Programa de obra")
    
    @api.one
    def fecha_calculo(self):
        if not self.fecha_avance or not self.fecha_informe:
            pass
        else:
            ff = datetime.strptime(str(self.fecha_informe), "%Y-%m-%d")
            ff1 = datetime.strptime(str(self.fecha_avance), "%Y-%m-%d")
            r = ff - ff1
            self.dias = r.days + 1

    @api.multi
    @api.onchange('a_fis', 'porcentajeProgramado')
    def cambiar_color(self):
        self.atraso = self.porcentajeProgramado - self.a_fis

        if self.atraso <= 5:
            self.color_semaforo = 'Verde'
        elif self.atraso > 5 and self.atraso <= 15:
            self.color_semaforo = 'Amarillo'
        else:
            self.color_semaforo = 'Rojo'

    @api.multi
    def boton_visual(self):
        print('nada')

    @api.multi
    def borrar(self):
        self.env['semaforo.contratos'].search([('id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class ComentariosObra(models.Model):
    _name = 'semaforo.comentarios_obra'

    partida = fields.Many2one('partidas.partidas')
    fecha_registro = fields.Date('Fecha')
    comentario = fields.Text('Comentario de Obra')


class CategoriasSemaforo(models.Model):
    _name = 'semaforo.categorias'
    _rec_name = 'tag'

    tag = fields.Char('Tag')
    partida_id = fields.Many2one('partidas.partidas', string="relacion a partida", store=True)