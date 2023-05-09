from odoo import api, fields, models, tools, _


class Galeria(models.Model):
    _name = 'avance.avance_fisico'
    _rec_name = 'imagen'

    imagen = fields.Binary(string="",  )
    frente = fields.Many2one('proceso.frente', string='FRENTE')

    id_partida = fields.Many2one('partidas.partidas', string='ID PARTIDA')

    _url = fields.Char(string="")

