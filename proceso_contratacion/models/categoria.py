from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class CatalogoNivel(models.Model):
    _name = "catalogo.categoria"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'

    id_sideop = fields.Integer('ID CATEGORIA SIDEOP')

    id_partida = fields.Many2one(comodel_name="partidas.partidas", string="Numero de partida", 
                                 store=True)

    # clave pedida por alan
    clave_linea = fields.Char('Clave')

    name = fields.Char('Categoria', index=True, translate=True)
    descripcion = fields.Text('Descripción', )
    parent_id = fields.Many2one('catalogo.categoria', 'Categoria Padre', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, readonly=True)
    child_id = fields.One2many('catalogo.categoria', 'parent_id', 'Child Categories', readonly=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True, readonly=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s.%s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]
