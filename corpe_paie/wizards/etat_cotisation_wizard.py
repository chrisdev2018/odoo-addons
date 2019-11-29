# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import Warning

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz

DATE_FORMAT = "%Y-%m-%d"
COLONNES = [
    'code_enregistrement', 'numero_dipe', 'cle_numero_dipe',
    'numero_contribuable', 'mois', 'numero_employeur',
    'cle_numero_employeur', 'regime_employeur', 'annee',
    'mat_cnps', 'cle_cnps', 'jour', 'sb', 'salex', 'sbt',
    'sc', 'irpp', 'tdl', 'matricule', 'name', 'prenom']

MOIS = [
    ('01', 'Janvier'),
    ('02', 'Fevrier'),
    ('03', 'Mars'),
    ('04', 'Avril'),
    ('05', 'Mai'),
    ('06', 'Juin'),
    ('07', 'Juillet'),
    ('08', 'Aout'),
    ('09', 'Septembre'),
    ('10', 'Octobre'),
    ('11', 'Novembre'),
    ('12', 'Decembre')]
ERREUR_FUSEAU = _("Indiquez votre fuseau horaire dans preferences")


class ResumeCotisationWizard(models.TransientModel):

    _name = 'corpe_paie.etat_cotisation_wizard'

    name = fields.Char(string="Nom du rapport")
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de fin")

    mois = fields.Selection(
        MOIS,
        string="Mois",
        default=lambda r: "%02d" % date.today().month)

    annee = fields.Integer(
        string="Annee",
        default=lambda r: "%d" % date.today().year)

    categorie_regle_sal = fields.Many2one(
        string="Categorie des retenues salariales",
        comodel_name="hr.salary.rule.category",
        required=True,
        default=lambda self: self.get_default_categorie(salariale=True))

    categorie_regle_pat = fields.Many2one(
        string="Categorie des retenues patronales",
        comodel_name="hr.salary.rule.category",
        required=True,
        default=lambda self: self.get_default_categorie(salariale=False))

    regle_sal_assiette = fields.Many2one(
        string="Regle assiette",
        comodel_name="hr.salary.rule",
        required=True,
        default=lambda self: self.get_default_regle_assiette())

    _centre = fields.Many2one(
        string="Centre/Etablissement",
        comodel_name="corpe_paie.centre_rh"
    )

    @api.model
    def get_default_categorie(self, salariale=True):
        code_categ = 'CHG_SAL' if salariale else 'CHG_PAT'
        return self.env['hr.salary.rule.category'].search(
            [('code', '=', code_categ)], limit=1)

    @api.model
    def get_default_regle_assiette(self):
        return self.env['hr.salary.rule'].search([('code', '=', 'SB')], limit=1)

    @api.multi
    def generate(self):
        """."""
        self.ensure_one()

        debut = date(self.annee, int(self.mois), 1)
        fin = debut + relativedelta(months=1, days=-1)

        now_utc = datetime.now(pytz.timezone('UTC'))
        if not self.env.user.tz:
            raise Warning(ERREUR_FUSEAU)
        # Convert to current user time zone
        date_heure = now_utc.astimezone(pytz.timezone(self.env.user.tz))

        datas = {}
        datas['debut'] = str(debut)
        datas['fin'] = str(fin)
        datas['name'] = self.name
        datas['mois'] = self.mois
        datas['annee'] = self.annee
        datas['code_centre'] = self._centre.code
        datas['categorie_regle_sal'] = self.categorie_regle_sal.id
        datas['categorie_regle_pat'] = self.categorie_regle_pat.id
        datas['regle_sal_assiette'] = self.regle_sal_assiette.code
        datas['date_impression'] = date_heure.strftime("%d/%m/%Y")
        datas['heure_impression'] = date_heure.strftime("%H:%M")
        datas['nom_centre'] = self._centre.name

        return {
            'type': 'ir.actions.report.xml',
            'report_name': "corpe_paie.etat_cotisation_template",
            'datas': datas}
