# -*- coding: utf-8 -*-
from openerp import api, fields, models


class CentreMaintenance(models.Model):
    _name = "corpe_maintenance.centre_maintenance"

    name = fields.Char(string="Nom",
                       default="",
                       required=True)

    warehouse = fields.Many2one(
        string="Rattache à",
        comodel_name="stock.warehouse")

    @api.onchange("warehouse")
    def _onchange_wharehouse(self):
        if self.warehouse:
            nom_entrepot = self.warehouse.name
            self.name = "Centre de maintenance de "+str(nom_entrepot)
