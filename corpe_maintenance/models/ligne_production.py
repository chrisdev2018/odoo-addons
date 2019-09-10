# -*- coding: utf-8 -*-
from openerp import api, fields, models


class LigneProduction(models.Model):
    _name = "corpe_maintenance.ligne_production"

    name = fields.Char(string="Nom",
                      required=True)

    centre = fields.Many2one(
        string="Centre",
        comodel_name="corpe_maintenance.centre_maintenance",
        required=True)

    code = fields.Char(
        string="Code",
        required=True
    )
