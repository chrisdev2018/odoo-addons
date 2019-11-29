# -*-coding: utf-8 -*-
from openerp import api, models
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp.exceptions import Warning


PAS_DE_BULLETIN = 'AUCUN BULLETIN DE PAIE NE CORRESPOND A VOTRE RECHERCHE'


def format_float(value, force_zero=False):
    if value != 0:
        return '{:,.2f}'.format(value).replace(',', ' ')
    else:
        return "" if not force_zero else "0"


class EtatCotisationReport(models.AbstractModel):
    _name = 'report.corpe_paie.etat_cotisation_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'corpe_paie.etat_cotisation_template')

        debut = data['debut']
        fin = data['fin']
        date_impression = data['date_impression']
        heure_impression = data['heure_impression']
        categorie_regle_sal = data['categorie_regle_sal']
        categorie_regle_pat = data['categorie_regle_pat']
        regle_sal_assiette = data['regle_sal_assiette']
        all_categories = [categorie_regle_sal, categorie_regle_pat]

        payslip_obj = self.env['hr.payslip']
        bulls = payslip_obj.search([
            ('date_from', '>=', debut),
            ('date_to', '<=', fin)])

        if data['code_centre']:
            bulls = bulls.filtered(
                lambda x: x.employee_id and x.employee_id.centre_rh_id and
                x.employee_id.centre_rh_id.code == data['code_centre'])

        if not bulls:
            raise Warning(PAS_DE_BULLETIN)

        result = []
        totaux = {}
        infos = {}

        infos['date_impression'] = date_impression
        infos['heure_impression'] = heure_impression
        infos['imprime_par'] = self.env.user.login
        infos['debut'] = "%s/%s/%s" % (debut[8:10], debut[5:7], debut[:4])
        infos['fin'] = "%s/%s/%s" % (fin[8:10], fin[5:7], fin[:4])
        if data['code_centre']:
            infos['entete_tableau'] = " " + data['code_centre'] + " CAMLAIT " + data['nom_centre']
        else:
            infos['entete_tableau'] = " CAMLAIT SA"

        totaux_salarial = 0
        totaux_patronal = 0
        totaux_global = 0

        lines_bulls = bulls.mapped('details_by_salary_rule_category').sorted(
            key=lambda r: r.sequence).filtered(
            lambda x: x.category_id.id in all_categories)
        lines_assiette = bulls.mapped('line_ids').filtered(
            lambda x: x.code == regle_sal_assiette)
        all_sequences = lines_bulls.mapped('sequence')
        for sequence in list(set(all_sequences)):
            lines_sequence = lines_bulls.filtered(
                lambda x: x.sequence == sequence)
            nbre_bulls = len(lines_sequence.mapped('slip_id'))
            employes = lines_sequence.mapped('slip_id.employee_id')

            nbre_hommes = len(employes.filtered(
                lambda x: x.gender == 'male'))
            nbre_femmes = len(employes.filtered(
                lambda x: x.gender == 'female'))

            if not lines_sequence:
                continue

            ligne_salarial = lines_sequence.filtered(
                lambda x: x.category_id.id == categorie_regle_sal)
            ligne_patronal = lines_sequence.filtered(
                lambda x: x.category_id.id == categorie_regle_pat)
            lignes_assiettes = lines_assiette.filtered(
                lambda x: x.slip_id.employee_id.id in employes.ids)

            taux_salarial = sum(ligne_salarial.mapped(
                'rate')) / nbre_bulls if nbre_bulls else 0
            taux_patronal = sum(ligne_patronal.mapped(
                'rate')) / nbre_bulls if nbre_bulls else 0
            taux_general = taux_salarial + taux_patronal

            assiette = sum(lignes_assiettes.mapped('total'))
            montant_salarial = sum(ligne_salarial.mapped('total'))
            montant_patronal = sum(ligne_patronal.mapped('total'))
            montant_general = montant_salarial + montant_patronal

            totaux_salarial += montant_salarial
            totaux_patronal += montant_patronal
            totaux_global += montant_general

            line = {}
            line['sequence'] = sequence
            line['rubrique'] = lines_sequence[0].name
            line['taux_sal'] = format_float(taux_salarial)
            line['taux_pat'] = format_float(taux_patronal)
            line['taux_gen'] = format_float(taux_general)
            line['assiette'] = format_float(assiette)
            line['base'] = format_float(sum(ligne_salarial.mapped('amount')))
            line['montant_salarial'] = format_float(montant_salarial)
            line['montant_patronal'] = format_float(montant_patronal)
            line['montant_global'] = format_float(montant_general)
            line['nbre_hommes'] = nbre_hommes
            line['nbre_femmes'] = nbre_femmes
            result.append(line)

        totaux['totaux_salarial'] = format_float(totaux_salarial)
        totaux['totaux_patronal'] = format_float(totaux_patronal)
        totaux['totaux_global'] = format_float(totaux_global)

        datas = {}
        datas['result'] = result
        datas['totaux'] = totaux
        datas['infos'] = infos

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': datas
        }

        return report_obj.render(
            'corpe_paie.etat_cotisation_template', docargs)
