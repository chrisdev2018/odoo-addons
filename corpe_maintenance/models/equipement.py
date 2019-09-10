# -*- coding: utf-8 -*-
from openerp import api, fields, models


class equipement(models.Model):
    _name = "corpe_maintenance.equipement"

    name = fields.Char(
        string="Nom",
        required=True)

    reference = fields.Char(
        string="Référence",
        size=64)

    ligne_id = fields.Many2one(
        string="Ligne de production",
        comodel_name="corpe_maintenance.ligne_production",
        required=True)

    marque = fields.Char(
        string="Marque")

    fabricant = fields.Char(
        string="Fabricant")

    mise_en_service = fields.Date(
        string="Date de mise en service")

    garantie = fields.Date(
        string="Date de fin de garantie")

    active = fields.Boolean(
        string="Actif",
        default=True)

    centre = fields.Char(
        string="Centre de maintenance",
        compute="_compute_centre",
        store=True
    )

    di_count = fields.Integer(
        string="D.I",
        compute="_count_for_buttons",
        readonly=True
    )

    bt_count = fields.Integer(
        string="B.T",
        compute="_count_for_buttons",
        readonly=True
    )

    activite_count = fields.Integer(
        string="Activités",
        compute="_count_for_buttons",
        readonly=True
    )

    dis = fields.One2many(
        string="Liste des DI",
        comodel_name="corpe_maintenance.demande_intervention",
        inverse_name="equipment",
        readonly=True
    )

    bts = fields.One2many(
        string="Liste des DI",
        comodel_name="corpe_maintenance.bon_travail",
        inverse_name="equipment",
        readonly=True
    )

    activites = fields.One2many(
        string="Liste des DI",
        comodel_name="corpe_maintenance.activite",
        inverse_name="equipment",
        readonly=True
    )

    @api.depends('ligne_id')
    def _compute_centre(self):
        self.centre = self.ligne_id.centre.name

    @api.multi
    def _count_for_buttons(self):
        for record in self:
            self.di_count = len(record.dis)
            self.bt_count = len(record.bts)
            self.activite_count = len(record.activites)

    @api.multi
    def open_di_tree(self):
        """Ouvre la vue tree des demandes d'intervention"""
        return {
            'name': ("Demandes d\'intervention sur l\'equipement  %s " % self.name),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'corpe_maintenance.demande_intervention',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': False,
            'domain': [('equipment', '=', self.id)]
        }

    @api.multi
    def open_bt_tree(self):
        """Ouvre la vue tree des demandes d'intervention"""
        return {
            'name': ("Bons de travail sur l\'equipement  %s " % self.name),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'corpe_maintenance.bon_travail',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': False,
            'domain': [('equipment', '=', self.id)]
        }

    @api.multi
    def open_activite_tree(self):
        """Ouvre la vue tree des demandes d'intervention"""
        return {
            'name': ("Activites sur l\'equipement  %s " % self.name),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'corpe_maintenance.activite',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': False,
            'domain': [('equipment', '=', self.id)]
        }
