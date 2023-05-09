from odoo import api, fields, models


class Residente(models.Model):
    _name = "partida.residente"
    _rec_name = 'residente'

    partida_id = fields.Many2one('partidas.partidas', string="id partida")
    residente = fields.Many2one('res.users', string="Residente")

    @api.multi
    def borrar(self):
        self.env['partida.residente'].search([('id', '=', self.id)]).unlink()