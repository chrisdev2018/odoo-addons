# -*- coding: utf-8 -*-

from openerp import api, models, fields
from openerp.exceptions import Warning

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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


class DipeNominalWizard(models.TransientModel):

    _name = 'corpe_paie.dipes_nominal_wizard'

    name = fields.Char(string="Nom du rapport")
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de fin")

    mois = fields.Selection(
        MOIS,
        string="Mois",
        default=lambda r: "%02d" % datetime.now().month)

    annee = fields.Integer(
        string="Annee",
        default=lambda r: "%d" % datetime.now().year)

    @api.multi
    def imprimer(self):
        self.ensure_one()

        debut = datetime.strptime(
            "%s-%s-01" % (self.annee, self.mois),
            DATE_FORMAT)
        fin = debut + relativedelta(months=1) - relativedelta(days=1)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'corpe_paie.statistiques_wizard.xls',
            'context': {
                'xls_export': 1,
                'colonnes': COLONNES,
                'title': self.name or "SANS TITRE",
                'debut': debut.strftime(DATE_FORMAT),
                'fin': fin.strftime(DATE_FORMAT)},
            'datas': {}}
