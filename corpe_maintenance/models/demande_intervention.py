# -*- coding: utf-8 -*-

from openerp import api, fields, models

priorites = [('basse', 'Basse'),
             ('normal', 'Normale'),
             ('haute', 'Haute')]

etats = [('marche', 'Marche'),
         ('arret', 'Arrêt'),
         ('degrade', 'Dégradé')]

states = [('new', 'Nouveau'),
          ('open', 'Ouvert'),
          ('closed', 'Cloturée'),
          ('rejected', 'Rejetée')]

symptomes_list = [
    ('usure', 'Usure'),
    ('fatigue', 'Fatigue'),
    ('surcharge', 'Surcharge'),
    ('surchauffe', 'Surchauffe'),
    ('reglage', 'Réglage'),
    ('corrosion', 'Corrosion'),
    ('utilisation', 'Mauvaise Utilisation')
]


class DemandeIntervention(models.Model):
    _name = "corpe_maintenance.demande_intervention"

    name = fields.Char(
        size=64,
        default="DI/",
        readonly=True,
        copy=False
    )

    type_panne = fields.Many2one(
        string="Type de panne",
        comodel_name="corpe_maintenance.type_panne"
    )

    emetteur = fields.Many2one(
        string="Emetteur",
        comodel_name="hr.employee",
        required=True)

    destinataire = fields.Many2one(
        string="Destinataire",
        comodel_name="hr.employee",
        required=True)

    priorite = fields.Selection(
        string="Priorité",
        selection=priorites,
        required=True,
        )

    symptomes = fields.Selection(
        size=64,
        selection = symptomes_list,
        string="Symptômes")

    date = fields.Date(
        string="Date Souhaitée",
        required=True)

    defaillance = fields.Char(
        string="Effet de la defaillance",
        size=64,
        required=True
    )

    localisation = fields.Char(
        string="Localisation",
        size=64)

    equipment = fields.Many2one(
        string="Equipement",
        comodel_name="corpe_maintenance.equipement",
        required=True
    )

    centre = fields.Char(
        string="Centre",
        compute="compute_centre"
        )

    etat = fields.Selection(
        string="Etat de l'équipement",
        selection=etats
    )

    state = fields.Selection(
        string="Statut",
        default='new',
        selection=states
    )

    # Methode qui valide la demande en generant sa reference
    @api.multi
    def action_di_open(self):
        for record in self:
            record.state = 'open'

            if record.name == "DI/":
                object_sequence = self.env["ir.sequence"]
                next_code = object_sequence.next_by_code('di.sequence', context=self.env.context)
                record.name = next_code
            else:
                record.name = record.name

    @api.multi
    def action_di_reject(self):
        for record in self:
            record.state = 'rejected'

    @api.multi
    def action_di_new(self):
        for record in self:
            record.state = 'new'

    @api.multi
    def action_di_to_bt(self):
        for rec in self:
            rec.state = 'closed'
            rec.generate_bt()

            # Ce return nous permet ici d'ouvrir la tree view des BT une fois la BT cree
            return {
                'name': 'Bon de travail',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'corpe_maintenance.bon_travail',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

    # Methode qui permet de generer le bon de travail
    # Sur la base de la demande d'intervention en cours
    @api.model
    def generate_bt(self):
        di_record_obj = self.env["corpe_maintenance.bon_travail"]

        values = {
            'equipment': self.equipment.id,
            'd_i': self.id,
            'etat': dict(self._fields['etat'].selection).get(self.etat),
            'symptomes': dict(self._fields['symptomes'].selection).get(self.symptomes),
            'emetteur': self.emetteur.id,
            'destinataire': self.destinataire.id
        }

        di_record_obj.create(values)

    @api.multi
    @api.depends('equipment')
    def compute_centre(self):
        for record in self:
            if record.equipment:
                record.centre = record.equipment.ligne_id.centre.name

