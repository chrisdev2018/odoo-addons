# -*-coding: utf-8 -*-
from openerp import api, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


def format_float(value, force_zero=False):
    if value != 0:
        return '{:,.0f}'.format(value).replace(',', ' ')
    else:
        return "" if not force_zero else "0"


class BulletinPaieReport(models.AbstractModel):
    _name = 'report.corpe_paie.bulletin_paie_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'corpe_paie.bulletin_paie_template')

        payslip_obj = self.env[report.model]
        payslip_line_obj = self.env['hr.payslip.line']
        bulls = payslip_obj.browse(self._ids)

        result = []

        for bull in bulls:
            elt = {}

            date_from = datetime.strptime(bull.date_from, '%Y-%m-%d')
            date_to = datetime.strptime(bull.date_to, '%Y-%m-%d')

            elt["period_date_from"] = date_from.strftime('%d/%m/%Y')
            elt["period_date_to"] = date_to.strftime('%d/%m/%Y')
            elt["methode_paiement"] = bull.contract_id.methode_paiement

            if bull.date_paiement:
                date_paiement = datetime.strptime(
                    bull.date_paiement, '%Y-%m-%d')
                elt["date_paiement"] = date_paiement.strftime('%d/%m/%Y')
            else:
                elt["date_paiement"] = ""

            elt["matricule"] = bull.contract_id.name
            elt["categorie"] = bull.contract_id.categorie
            elt["emploi"] = bull.contract_id.job_id and \
                bull.contract_id.job_id.name or ""
            elt["departement"] = bull.employee_id.department_id and \
                bull.employee_id.department_id.name or ""
            elt["nom_centre"] = "CAMLAIT " + bull.employee_id.centre_rh_id.name if \
                bull.employee_id.centre_rh_id else "CAMLAIT NaN"
            
            elt["qualification"] = ""
            elt["horaire"] = ""
            elt["convention"] = ""
            elt["nom"] = bull.employee_id.name
            elt["prenom"] = bull.employee_id.prenom

            if bull.employee_id.gender:
                if bull.employee_id.gender == "female":
                    if bull.employee_id.marital:
                        if bull.employee_id.marital == "single":
                            elt["nome"] = "Mlle."
                        else:
                            elt["nome"] = "Mme."
                    else:
                        elt["nome"] = ""

                else:
                    elt["nome"] = "M."
            else:
                elt["nome"] = ""

            elt["secu_sociale"] = str(bull.employee_id.mat_cnps) + " - " if bull.employee_id.mat_cnps else " - "
            elt["secu_sociale"] += str(bull.employee_id.cle_cnps)

            # recupere les infos de la grille
            elt["niveau"] = ""
            elt["coefficient"] = ""
            elt["indice"] = ""
            grille = bull.grille_salariale
            if grille:
                elt["niveau"] = grille.categ_id.code
                elt["coefficient"] = grille.ech_id.code
                elt["indice"] = str(grille.ech_id.num_ordre)

            # recupere l'anciennete
            elt["anciennete"] = ""
            date_start = bull.contract_id.date_start

            if date_start and len(date_start) > 9:
                object_date_start = datetime.strptime(
                    date_start[:10], "%Y-%m-%d")
                object_date_start = object_date_start.replace(day=1)
                fin_mois = datetime.strptime(bull.date_to[:10], "%Y-%m-%d")
                fin_mois += relativedelta(days=1)
                diff = relativedelta(fin_mois, object_date_start)
                elt["anciennete"] += str(diff.years)
                elt["anciennete"] += " an(s) " if diff.years > 1 else " an"
                elt["anciennete"] += " %s mois" % str(diff.months)

            elt["gains"] = []
            for ligne in bull.line_ids.filtered(
                    lambda x: x.sequence < 999 and
                    x.salary_rule_id.appears_on_payslip):
                gain = "ded" not in ligne.category_id.code.lower()
                elt_gain = {}
                elt_gain["n"] = ligne.sequence
                elt_gain["designation"] = ligne.name
                elt_gain["nombre"] = ligne.quantity
                elt_gain["base"] = format_float(ligne.amount)
                elt_gain["taux"] = ligne.rate
                elt_gain["gain"] = format_float(ligne.total) if gain else ""
                elt_gain["retenue"] = "" if gain else format_float(ligne.total)
                elt["gains"].append(elt_gain)

            brut = bull.line_ids.filtered(lambda x: x.sequence == 999)
            elt['brut'] = {}
            elt['brut']["n"] = brut.sequence
            elt['brut']["designation"] = "Total Brut"
            elt['brut']["nombre"] = ""
            elt['brut']["base"] = ""
            elt['brut']["taux"] = ""
            elt['brut']["gain"] = format_float(brut.total)
            elt['brut']["retenue"] = ""

            elt["chrgs_sal"] = []
            regles_charges_sal = bull.line_ids.filtered(
                lambda x: x.category_id.code == 'CHG_SAL' and
                x.salary_rule_id.appears_on_payslip)
            for ligne in regles_charges_sal:
                elt_sal = {}
                elt_sal["n"] = ligne.sequence
                elt_sal["designation"] = ligne.name
                elt_sal["nombre"] = ligne.quantity
                elt_sal["base"] = format_float(ligne.amount)
                elt_sal["taux"] = ligne.rate
                elt_sal["gain"] = ""
                elt_sal["retenue"] = format_float(ligne.total)
                elt_sal["p_taux"] = ""
                elt_sal["p_gain"] = ""
                elt_sal["p_retenue"] = ""

                # recuperer les elements pat
                regle_pat = bull.line_ids.filtered(
                    lambda x: x.sequence == ligne.sequence and
                    x.code != ligne.code)
                if regle_pat:
                    elt_sal["p_taux"] = regle_pat[0].rate
                    elt_sal["p_gain"] = ""
                    elt_sal["p_retenue"] = format_float(regle_pat[0].total)

                elt["chrgs_sal"].append(elt_sal)

            tot_cot_sal = bull.details_by_salary_rule_category.filtered(
                lambda x: x.code == "TOT_COT_SAL")
            tot_cot_pat = bull.details_by_salary_rule_category.filtered(
                lambda x: x.code == "TOT_COT_PAT")
            elt['tot_cot'] = {}
            elt['tot_cot']["n"] = ""
            elt['tot_cot']["designation"] = "Total cotisations"
            elt['tot_cot']["nombre"] = ""
            elt['tot_cot']["base"] = ""
            elt['tot_cot']["taux"] = ""
            elt['tot_cot']["gain"] = ""
            elt['tot_cot']["retenue"] = format_float(tot_cot_sal.total)
            elt['tot_cot']["p_taux"] = ""
            elt['tot_cot']["p_gain"] = ""
            elt['tot_cot']["p_retenue"] = format_float(tot_cot_pat.total)

            elt["divers"] = []
            regles_divers = bull.line_ids.filtered(
                lambda x: x.category_id.code == 'DIVERS' and
                x.salary_rule_id.appears_on_payslip)
            for ligne in regles_divers:
                elt_div = {}
                elt_div["n"] = ligne.sequence
                elt_div["designation"] = ligne.name
                elt_div["nombre"] = ""
                elt_div["base"] = ""
                elt_div["taux"] = ""
                elt_div["gain"] = ""
                elt_div["retenue"] = format_float(ligne.total)
                elt_div["p_taux"] = ""
                elt_div["p_gain"] = ""
                elt_div["p_retenue"] = ""
                elt["divers"].append(elt_div)

            # recupere les infos generales du bulletin
            regles_detailes = bull.details_by_salary_rule_category
            sit = regles_detailes.filtered(lambda x: x.code == "SIT")
            tot_chrgs_sal = regles_detailes.filtered(
                lambda x: x.code == "TOT_COT_SAL")
            tot_chrgs_pat = regles_detailes.filtered(
                lambda x: x.code == "TOT_COT_PAT")
            net_a_payer = regles_detailes.filtered(lambda x: x.code == "NAP")

            hsupp = sum(regles_detailes.filtered(
                lambda x: x.code.lower() in ['hs20', 'hs30', 'hs40', 'hs50']).mapped(
                'quantity'))

            reg_voiture = regles_detailes.filtered(
                lambda x: x.code == "VOITURE")
            reg_logemen = regles_detailes.filtered(
                lambda x: x.code == "LOGEMENT")
            avant = reg_voiture.total + reg_logemen.total

            elt['infos'] = {}
            elt['infos']['brut'] = format_float(brut.total)
            elt['infos']['sit'] = format_float(sit.total)
            elt['infos']['tot_chrgs_sal'] = format_float(tot_chrgs_sal.total)
            elt['infos']['tot_chrgs_pat'] = format_float(tot_chrgs_pat.total)
            elt['infos']['net_a_payer'] = format_float(net_a_payer.total)
            elt['infos']['avantage'] = format_float(avant, force_zero=True)
            elt['infos']['hsupp'] = format_float(hsupp, force_zero=True)

            year = datetime.now().year
            lines_cumuls = payslip_line_obj.search([
                ('employee_id', '=', bull.employee_id.id),
                ('slip_id.date_from', '>=', str(year) + '-01-01'),
                ('slip_id.date_to', '<=', bull.date_to),
                ('code', 'in', [
                    'SB', 'SIT', 'TOT_COT_SAL', 'TOT_COT_PAT', 'NAP',
                    'VOITURE', 'LOGEMENT', 'HS20', 'HS30', 'HS40', 'HS50'])])

            cumul_brut = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'sb').mapped('total'))
            cumul_sit = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'sit').mapped('total'))
            cumul_cotsal = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'tot_cot_sal').mapped('total'))
            cumul_cotpat = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'tot_cot_pat').mapped('total'))
            cumul_voiture = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'voiture').mapped('total'))
            cumul_logement = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'logement').mapped('total'))
            cumul_heure_sup = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() in ['hs20', 'hs30', 'hs40', 'hs50']).mapped(
                'quantity'))
            cumul_avan = cumul_voiture + cumul_logement
            nap = sum(lines_cumuls.filtered(
                lambda x: x.code.lower() == 'nap').mapped('total'))
            nbre_slip = len(lines_cumuls.mapped("slip_id"))

            elt['infos']['cumul_brut'] = format_float(cumul_brut)
            elt['infos']['cumul_sit'] = format_float(cumul_sit)
            elt['infos']['cumul_cotsal'] = format_float(cumul_cotsal)
            elt['infos']['cumul_cotpat'] = format_float(cumul_cotpat)
            elt['infos']['cumul_hsupp'] = format_float(
                cumul_heure_sup, force_zero=True)
            elt['infos']['cumul_avan'] = format_float(
                cumul_avan, force_zero=True)
            elt['infos']['cumul_travail'] = format_float(
                173 * nbre_slip, force_zero=True)
            elt['infos']['nap'] = format_float(nap)
            result.append(elt)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': result
        }
        return report_obj.render(
            'corpe_paie.bulletin_paie_template', docargs)
