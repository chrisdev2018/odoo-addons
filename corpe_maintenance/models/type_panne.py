# -*- coding: utf-8 -*-

from openerp import api, fields, models


class typePanne(models.Model):
    _name = "corpe_maintenance.type_panne"

    name = fields.Char(
        string="Titre")
    code = fields.Char(
        string="code")
    description = fields.Text(
        string="Description")
