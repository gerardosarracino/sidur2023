from odoo import models, fields, api, exceptions
from datetime import datetime
import calendar
import datetime


class ProgramaObra(models.Model):
    _name = 'programa.programa_obra'
    _rec_name = 'obra'

    # IMPORTACION
    id_prog = fields.Integer(string="ID PROGRAMA", required=False, )

    # TERMINA IMPORTACION
    obra = fields.Many2one('partidas.partidas', string='Obra:', store=True)

    obraid = fields.Many2one('partidas.partidas', string='Obra:', readonly=True)
    obra_id = fields.Char(compute="partidaEnlace", store=True)
    obra_id2 = fields.Char(compute="partidaEnlaceId", store=True)

    fecha_inicio_programa = fields.Date('Fecha Inicio:', related="obra.numero_contrato.fechainicio")
    fecha_termino_programa = fields.Date('Fecha Término:', related="obra.numero_contrato.fechatermino")

    # CUANDO HAYA CONVENIO DE PLAZO MOSTRAR ESTAS FECHAS
    fecha_inicio_convenida = fields.Date('Fecha Inicio:', related="obra.fecha_inicio_convenida" ) #  compute="b_convenio_plazo"
    fecha_termino_convenida = fields.Date('Fecha Inicio:', related="obra.fecha_termino_convenida" ) #  compute="b_convenio_plazo"

    # FECHAS CONTINUAS
    inicio_anterior = fields.Date('Fecha Inicio Anterior', store=True)
    termino_nueva = fields.Date('Fecha Termino Nueva', store=True)

    # ULTIMAS FECHAS
    ultima_fecha_inicio = fields.Date('Fecha Inicio', store=True)
    ultima_fecha_termino = fields.Date('Fecha Termino', store=True)


    @api.multi
    @api.onchange('programa_contratos')
    def ultimas_fechas(self):
        ultima_fecha_inicio = ""
        ultima_fecha_termino = ""
        acum = 0
        for x in self.programa_contratos:
            if x.fecha_inicio:
                acum += 1
        print(acum)
        if acum == 0:
            pass
        else:
            for i in self.programa_contratos:
                dia_ultimo_mes = calendar.monthrange(i.fecha_termino.year, i.fecha_termino.month)[1]
                fechax_ = str(i.fecha_termino)
                ff = str(fechax_[8] + fechax_[9])
                ff_int = int(ff)
                if int(dia_ultimo_mes) == int(ff_int):
                    fff = str(fechax_[5] + fechax_[6])
                    dd = int(fff) + 1

                    anio = str(fechax_[2] + fechax_[3])

                    if len(str(dd)) >= 2:
                        dds = str(dd)
                    else:
                        dds = '0' + str(dd)

                    if dd == 13:
                        dds = '01'
                        aniox = int(anio) + 1
                        anio = str(aniox)

                    mm = '01'
                    fechay_ = fechax_[0] + fechax_[1] + anio[0] + anio[1] + fechax_[
                        4] + dds[0] + dds[1] + fechax_[7] + mm[0] + mm[1]

                    ultima_fecha_inicio = fechay_

                    fechay_x = datetime.datetime.strptime(str(ultima_fecha_inicio), '%Y-%m-%d')

                    dia_ultimo_mesx = calendar.monthrange(fechay_x.year, fechay_x.month)[1]
                    dia = str(dia_ultimo_mesx)
                    fecha_final_ = str(fechay_)

                    fecha_final = fecha_final_[0] + fecha_final_[1] + fecha_final_[2] + fecha_final_[3] + fecha_final_[
                        4] + fecha_final_[5] + fecha_final_[6] + fecha_final_[7] + dia[0] + dia[1]
                    ultima_fecha_termino = fecha_final
                else:
                    fecha_i_ = str(i.fecha_termino)

                    dia_s = str(fecha_i_[8] + fecha_i_[9])

                    dias_sint = int(dia_s) + 1
                    if len(str(dias_sint)) >= 2:
                        dias_str = str(dias_sint)
                    else:
                        dias_str = '0' + str(dias_sint)

                    fecha_i = fecha_i_[0] + fecha_i_[1] + fecha_i_[2] + fecha_i_[3] + fecha_i_[4] + fecha_i_[5] + \
                              fecha_i_[6] + fecha_i_[7] + dias_str[0] + dias_str[1]

                    ultima_fecha_inicio = fecha_i

                    dia = str(dia_ultimo_mes)
                    fecha_final_ = str(i.fecha_termino)

                    fecha_final = fecha_final_[0] + fecha_final_[1] + fecha_final_[2] + fecha_final_[3] + fecha_final_[
                        4] + fecha_final_[5] + fecha_final_[6] + fecha_final_[7] + dia[0] + dia[1]

                    ultima_fecha_termino = fecha_final

        self.ultima_fecha_inicio = ultima_fecha_inicio
        self.ultima_fecha_termino = ultima_fecha_termino

    restante_programa = fields.Float(string="Restante:", compute='DiferenciaPrograma')
    programa_contratos = fields.Many2many('proceso.programa', string="Agregar Periodo:")

    # TOTAL DEL PROGRAMA CON O SIN CONVENIO
    total_partida = fields.Float(string="Total", related="obra.total")  # related="obra.total_catalogo" compute="total_programa_convenio"

    # HISTORIAL
    razon = fields.Text(string="Versión:", required=False, default="")
    select_tipo = [('Monto', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:", store=True)

    total_programa = fields.Float(compute="totalPrograma",)

    estatus_programa = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado'), ('validado', 'Validado'), ],
        default='borrador')

    '''conv_contador = fields.Integer(compute="b_convenio_plazo")

    # BUSCAR SI HAY CONVENIO MODIFICATORIO DE PLAZO
    @api.one
    def b_convenio_plazo(self):
        b_convenio_contador = self.env['proceso.convenios_modificado'].search_count([('contrato.id', '=', self.obra.id)])
        self.conv_contador = b_convenio_contador
        b_convenio = self.env['proceso.convenios_modificado'].search([('contrato.id', '=', self.obra.id)])
        if b_convenio_contador > 0:
            for i in b_convenio:
                if i.tipo_convenio == 'PL' or i.tipo_convenio == 'BOTH':
                    self.fecha_inicio_convenida = i.plazo_fecha_inicio
                    self.fecha_termino_convenida = i.plazo_fecha_termino
                else:
                    print('pasar')'''

    @api.one
    def totalPrograma(self):
        acum = 0
        for i in self.programa_contratos:
            acum = acum + i.monto
            self.total_programa = acum

    '''@api.multi
    def write(self, values):
        print('--')
        if self.total_programa == self.total_partida:
            print('si pasa')
        else:
            print('3')
            raise exceptions.Warning('El monto del programa no es igual al del contrato!!!,')
        # values['idobra'] = str(num)
        print('-----')
        return super(ProgramaObra, self).write(values)'''

    @api.one
    def borrador_progressbar(self):
        self.write({'estatus_programa': 'borrador', })

    @api.one
    def confirmado_progressbar(self):
        self.write({'estatus_programa': 'confirmado'})

    @api.one
    def validado_progressbar(self):
        self.write({'estatus_programa': 'validado'})

    '''@api.multi
    def write(self, values):
        if not self.tipo:
            raise exceptions.Warning('Haz realizado una modificación al programa!!!,')
        elif not self.razon:
            raise exceptions.Warning('Haz realizado una modificación al programa!!!,'
                                     ' Porfavor escriba la razon del cambio.')
                 if self.restante_programa == 0:
            print('si')
        else:
            raise exceptions.Warning('el monto!!!,')
        version = self.env['programa.programa_version']
        id_programa = self.id
        datos = {'comentario': values['razon'], 'programa': id_programa, 'tipo': values['tipo']}
        nueva_version = version.create(datos)
        values['razon'] = ""
        values['tipo'] = ""
        return super(ProgramaObra, self).write(values)'''

    @api.one
    def partidaEnlace(self):
        self.obra_id = self.obra

    @api.one
    def partidaEnlaceId(self):
        self.obra_id2 = self.obraid

    '''@api.multi
    @api.onchange('total_partida')
    def BmontoContrato(self):
        b_partida = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])
        self.monto_sinconvenio = b_partida.monto_sin_iva'''

    '''@api.one
    def total_programa_convenio(self):
        count_convenio = self.env['proceso.convenios_modificado'].search_count([('contrato.id', '=', self.obra.id)])
        self.count_convenio = count_convenio
        importe_convenio = self.env['proceso.convenios_modificado'].search([('contrato.id', '=', self.obra.id)])

        # b_partida = self.env['partidas.partidas'].search([('id', '=', self.obra.id)])

        if count_convenio >= 1:
            for i in importe_convenio:
                self.total_partida = i.monto_importe
        else:
            self.total_partida = self.monto_sinconvenio'''

    '''@api.multi
    @api.onchange('programa_contratos')
    def SumaProgramas(self):
        suma = 0
        for i in self.programa_contratos:
            resultado = i.monto
            suma = suma + resultado
            self.monto_programa_aux = suma'''

    # METODO PARA SACAR LA FECHA DEL M2M
    @api.one
    @api.depends('programa_contratos')
    def fechaTermino(self):
        for i in self.programa_contratos:
            resultado = str(i.fecha_termino)
            self.fecha_termino_programa = str(resultado)

    @api.one
    def DiferenciaPrograma(self):
        restante_programa = self.total_partida - self.total_programa
        self.restante_programa = round(restante_programa, 2)


# CLASE NUEVA
class ProgramaVersion(models.Model):
    _name = 'programa.programa_version'
    _rec_name = 'programa'

    select_tipo = [('1', 'Monto'), ('2', 'Plazo'), ('3', 'Ambos')]
    tipo = fields.Selection(select_tipo, string="Tipo:")
    fecha = fields.Date('Fecha:', default=fields.Date.today())
    programa = fields.Many2one('programa.programa_obra', string="Programa:")
    comentario = fields.Text(string="Comentario:", required=False, )


class TablaPrograma(models.Model):
    _name = 'programa.tabla'

    fecha_inicio = fields.Date()
    fecha_termino = fields.Date()
    monto = fields.Float()

