# -*- coding: utf-8 -*-

from openerp import api, fields, models

priorites = [('basse', 'Basse'),
             ('normal', 'Normale'),
             ('haute', 'Haute')]

states = [('new', 'Nouveau'),
          ('open', 'En cours'),
          ('closed', 'Terminé')]


class BonTravail(models.Model):
    _name = "corpe_maintenance.bon_travail"

    name = fields.Char(
        string="Réference",
        default="BT/",
        copy=False,
        readonly=True
    )

    d_i = fields.Many2one(
        string="Demande d'intervention",
        comodel_name="corpe_maintenance.demande_intervention",
        readonly=True,
    )

    equipment = fields.Many2one(
        string="Equipement",
        comodel_name="corpe_maintenance.equipement",
        readonly=True
    )

    etat = fields.Char(
        string="Etat de l'equipement",
        readonly=True
    )

    symptomes = fields.Char(
        string="Symptômes",
        readonly=True
    )

    emetteur = fields.Many2one(
        string="Emetteur",
        comodel_name="hr.employee",
        readonly=True
    )

    destinataire = fields.Many2one(
        string="Destinataire",
        comodel_name="hr.employee",
        readonly=True
    )

    intervenant = fields.Many2one(
        string="Intervenant",
        comodel_name="hr.employee",
        required=False
    )

    priorite = fields.Selection(
        string="Priorité",
        selection=priorites,
        required=False
    )

    projet = fields.Many2one(
        string="Projet",
        comodel_name="project.project"
    )

    taf = fields.Text(
        string="Travail à faire"
    )

    state = fields.Selection(
        string="Statut",
        default='new',
        selection=states
    )

    @api.multi
    def action_open_bt(self):
        for rec in self:
            rec.state = 'open'

            object_sequence = self.env["ir.sequence"]
            next_code = object_sequence.next_by_code('bt.sequence', context=self.env.context)
            rec.name = next_code

    @api.multi
    def action_close_bt(self):
        for rec in self:
            rec.state = 'closed'
            rec.generate_activity()

            # Ce return nous permet ici d'ouvrir la tree view des fiches d'activite une fois la fiche cree
            return {
                'name': 'Fiche d\'activite',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'corpe_maintenance.activite',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

    @api.model
    def generate_activity(self):
        di_record_obj = self.env["corpe_maintenance.activite"]

        values = {
            'equipment': self.equipment.id,
            'bt': self.id
        }

        di_record_obj.create(values)
