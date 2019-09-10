# -*- coding: utf-8 -*-
from openerp import api, fields, models


class PieceRechangeLine(models.Model):
    _name = "corpe_maintenance.piece_rechange_line"

    product_id = fields.Many2one(
        string="Article",
        comodel_name="product.template",
        domain="[('est_piece_rechange','=',True)]"
    )

    quantite = fields.Integer(
        string="Quantite",
        default=0
    )

    unite = fields.Char(
        string="Unite de mesure",
    )

    prix_unitaire = fields.Integer(
        string="Prix unitaire",
        default=0
    )

    activite_id = fields.Many2one(
        comodel_name="corpe_maintenance.activite"
    )

    @api.onchange('product_id')
    def _onchange_article(self):
        self.unite = self.product_id.uom_id.name
        self.prix_unitaire = self.product_id.lst_price
