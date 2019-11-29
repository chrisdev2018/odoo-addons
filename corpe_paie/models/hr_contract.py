# -*- coding: utf-8 -*-
from openerp import api, fields, models
from datetime import datetime
from dateutil.relativedelta import *


class HrContract(models.Model):

    _inherit = 'hr.contract'

    primes_ind = fields.One2many(
        string='Primes et Indemnites',
        help="Primes de ce contrat",
        comodel_name='corpe_paie.prime_ind',
        inverse_name="contrat_id",
        track_visibility='onchange')

    # Rajout
    methode_paiement = fields.Selection(
        string="Methode de paiement",
        selection=[
            ("virement", "Virement"),
            ("espece", "Espece"),
            ("carte", "Carte"),
            ("cheque", "Cheque")])

    categorie = fields.Char(string="Categorie de l'employe")

    grille_salaire = fields.Many2one(
        string='Grille salariale',
        readonly=False,
        required=False,
        help="grille salariale de ce contrat",
        comodel_name='corpe_paie.grille_salaire',
        track_visibility='onchange')

    # Rajout
    anciennete = fields.Integer(
        compute='calcul_anciennete',
        string='Anciennete',
        readonly=True)

    # Rajout
    base_indice = fields.Float(
        string='Salaire de base Indiciel',
        readonly=False)

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account')

    personal_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Compte personnel')

    @api.onchange('type_id')
    def onchange_type_id(self):
        domain = []
        if self.type_id:
            grilles_ids = self.type_id.grilles_salaire.mapped('id')
            domain = [('id', 'in', grilles_ids)]
        return {'domain': {'grille_salaire': domain}}

    @api.onchange("grille_salaire")
    def onchange_grille_salaire(self):
        self.wage = self.grille_salaire.montant

    @api.multi
    def unlink(self):
        grilles = self.mapped('grille_salaire')
        res = super(HrContract, self).unlink()
        grilles.update_masse()
        return res

    @api.multi
    def update_salary(self):
        for record in self:
            if record.grille_salaire:
                record.wage = record.grille_salaire.montant

    @api.constrains('grille_salaire', 'wage')
    def check_update_masse(self):
        for record in self:
            if record.grille_salaire:
                record.grille_salaire.update_masse()


# Calcul de l'anciennete en nombre d'annees

    @api.depends('date_start')
    def calcul_anciennete(self):
        for record in self:
            record.anciennete = 0
            if record.date_start:
                today = datetime.now().date()

                start_date = record.date_start

                today_date = str(today)

                start = datetime.strptime(start_date, '%Y-%m-%d')

                end = datetime.strptime(today_date, '%Y-%m-%d')

                diff = relativedelta(end, start)

                record.anciennete = (diff.years)


# Definition du salaire de base indicielle

    @api.onchange("grille_salaire")
    def onchange_grille_salaire_(self):
        for record in self :
            if record.grille_salaire:
                for grille in self.env['corpe_paie.grille_salaire'].search([]):
                    if grille.categ_id.code == record.grille_salaire.categ_id.code and grille.ech_id.code == 'A':
                        record.base_indice = grille.montant
                        break
