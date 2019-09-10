# -*- coding: utf-8 -*-
from openerp import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta

etats = [("new", "Nouveau"),
         ("opened", "Ouvert"),
         ("closed", "Fermé")
         ]

correction_list = [
    ('reparation', 'Réparation'),
    ('depannage', 'Dépannage'),
    ('amelioration', 'Amélioration'),
    ('entretien', 'Entretien '),
    ('preventif', 'préventif'),
    ('installation', 'nouvelle installation')
]

diagnostic_list = [
    ('usure', 'Usure'),
    ('accident ', 'Accident'),
    ('imprevu', 'Imprévu'),
    ('corrosion', 'Corrosion'),
    ('fabrication', 'Défaut de fabrication'),
    ('reglage', 'Mauvais réglage')
]


class Activite(models.Model):
    _name = "corpe_maintenance.activite"

    name = fields.Char(
        string="N° Fiche",
        size=64,
        default="Activite/",
        copy=False,
        readonly=True
    )

    state = fields.Selection(
        string="Statut",
        selection=etats,
        default="new"
    )

    equipment = fields.Many2one(
        string="Equipement",
        comodel_name="corpe_maintenance.equipement",
        readonly=True
    )

    bt = fields.Many2one(
        string="Bon de Travail",
        comodel_name="corpe_maintenance.bon_travail",
        readonly=True,
    )

    diagnostic = fields.Selection(
        size=64,
        selection=diagnostic_list,
        string="Diagnostic"
    )

    correction = fields.Selection(
        string="Correction",
        selection=correction_list,
        size=64
    )

    debut = fields.Datetime(
        string="Date de debut",
    )

    fin = fields.Datetime(
        string="Date de fin"
    )

    date = fields.Date(
        string="Date de création"
    )

    observation = fields.Text(
        string="Observation"
    )

    duree = fields.Integer(
        string="Temps passé(en h)",
        readonly=True,
        compute='compute_duree',
        stored=True
    )

    indisponibilite = fields.Integer(
        string="Temps d'indisponiblité (en h)",

    )

    piece_lines = fields.One2many(
        string="piece_rechange",
        comodel_name="corpe_maintenance.piece_rechange_line",
        inverse_name="activite_id"
    )

    intervenant_lines = fields.One2many(
        string="Intervenants",
        comodel_name="corpe_maintenance.intervenant_line",
        inverse_name="activite_id"
    )

    @api.depends('debut', 'fin')
    def compute_duree(self):
        if (self.debut and self.fin) and (len(self.debut) > 9 and len(self.fin) > 9):
            object_date_start = datetime.strptime(self.debut[:13], "%Y-%m-%d %H")
            object_date_fin = datetime.strptime(self.fin[:13], "%Y-%m-%d %H")
            diff = relativedelta(object_date_fin, object_date_start)

            self.duree = (diff.days * 24) + diff.hours

    @api.multi
    def action_act_confirm(self):
        for record in self:
            record.state = "closed"

    @api.multi
    def action_act_reopen(self):
        for rec in self:
            rec.state = "opened"

    @api.multi
    def action_act_open(self):
        for rec in self:
            object_sequence = self.env["ir.sequence"]
            next_code = object_sequence.next_by_code('activite.sequence', context=self.env.context)
            rec.name = next_code

            rec.state = "opened"