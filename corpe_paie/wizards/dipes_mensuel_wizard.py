# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
from openerp.exceptions import Warning
import unicodedata

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

DATE_FORMAT = "%Y-%m-%d"
NO_PAYSLIP_FOUND = _("Aucun bulletin de paie dans la periode")

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


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class DipesMensuelWizard(models.TransientModel):

    _name = 'corpe_paie.dipes_mensuel_wizard'

    mois = fields.Selection(
        MOIS,
        string="Mois",
        default=lambda r: "%02d" % datetime.now().month)

    annee = fields.Integer(
        string="Annee",
        default=lambda r: "%d" % datetime.now().year)

    employees = fields.Many2many(
        'hr.employee',
        relation="wizdipes_rel_employee")

    bulletins = fields.Many2many(
        'hr.payslip',
        relation="wizdipes_rel_payslip")

    @api.multi
    def generate(self):
        self.ensure_one()

        debut = datetime.strptime(
            "%s-%s-01" % (self.annee, self.mois),
            DATE_FORMAT)
        fin = debut + relativedelta(months=1) - relativedelta(days=1)

        payslip_line_obj = self.env['hr.payslip.line']
        domain = []
        if debut and fin:
            domain.append(('slip_id.date_from', '>=', debut.date()))
            domain.append(('slip_id.date_to', '<=', fin.date()))
        all_objs = payslip_line_obj.search(domain)
        if not all_objs:
            raise Warning(NO_PAYSLIP_FOUND)
        employees = all_objs.mapped('employee_id').sorted(
            lambda x: x.contract_id.name if x.contract_id else "")

        dipes = []
        i = 1

        company_obj = self.env['res.company']
        ste = company_obj.search([], limit=1)

        sortie = ""
        sortie += "C04"
        sortie += ("%5s" % ste.numero_dipe if ste.numero_dipe else '00000')[:5]
        sortie += (str(ste.cle_numero_dipe) if ste.cle_numero_dipe else '_')[:1]
        sortie += ("%14s" % ste.numero_contribuable if ste.numero_contribuable else '______________')[:14]
        sortie += "MOIS"
        sortie += ("%10s" % ste.numero_employeur if ste.numero_employeur else '__________')[:10]
        sortie += (ste.cle_numero_employeur if ste.cle_numero_employeur else '_')[:1]
        sortie += ("%1d" % ste.regime_employeur if ste.regime_employeur else '_')[:1] # regime cnps ou regime employeur
        sortie += "ANNEE_DIPES"
        sortie += "_NUMERO_CNPS_"
        sortie += "_CLE_NUM_CNPS_"
        sortie += "NOMBRE_JOUR"
        sortie += "SALAIRE_BRUT" # salaire brut
        sortie += "_SALAIRE_EXCEPTIONNEL_"
        sortie += "SALAIRE_TAXABLE" # salaire taxable
        sortie += "SALAIRE_CNPS" # salaire cotisable cnps
        sortie += "SALAIRE_PLAFONNE" # salaire cotisable plafonne
        sortie += "_IRPP_" # retenue irpp
        sortie += "_TC_" # retenue taxe communale
        sortie += "LIGNE" # numero de ligne
        sortie += "_MATRICULE_"
        sortie += "_NOMPRENOM_"

        for elt in employees:
            ligne_col = int(i % 16) if (i % 16) != 0 else 16

            obbj = {}
            all_objs_emp = all_objs.filtered(
                lambda x: x.employee_id.id == elt.id)
            for ligne in all_objs_emp:
                key = ligne.code.lower().replace("/", "_")
                if key in obbj.keys():
                    obbj[key] += ligne.total
                else:
                    obbj[key] = ligne.total
            objet = Struct(**obbj)

            salaire_brut = 0
            salaire_taxa = 0
            salaire_cnps = 0
            salaire_plaf = 0
            irpp = 0
            taxe_comm = 0
            valeur = None
            bulletin = all_objs_emp[0].slip_id if all_objs_emp else None

            salaire_brut = objet.sb if hasattr(objet, 'sb') else 0
            salaire_excep = objet.salex if hasattr(objet, 'salex') else 0
            salaire_taxa = objet.sbt if hasattr(objet, 'sbt') else 0
            salaire_cnps = objet.sc if hasattr(objet, 'sc') else 0
            salaire_plaf = objet.sc if hasattr(objet, 'sc') else 0
            salaire_plaf = salaire_plaf if salaire_plaf < 750000 else 750000
            diffrence_jour = objet.jour if hasattr(objet, 'jour') else 0
            irpp = objet.irpp if hasattr(objet, 'irpp') else 0
            taxe_comm = objet.tdl if hasattr(objet, 'tdl') else 0
            matricule = elt.contract_id.name if elt.contract_id else ""

            name_encoded = unicode(elt.name if elt.name else u"")
            prenom_encoded = unicode(elt.prenom if elt.prenom else u"")
            nomprenom = ("%s %s" % (name_encoded, prenom_encoded)).strip()

            diff_caratere_matricule = 14 - len(matricule)
            matricule = str("0" * diff_caratere_matricule) + matricule
            if elt.mat_cnps:
                cle_cnps = elt.cle_cnps if elt.cle_cnps else "0"
            else:
                cle_cnps = " "

            valeur = sortie
            valeur = valeur.replace('_NUMERO_CNPS_', ('%10s' % (elt.mat_cnps if elt.mat_cnps else ""))[:10])
            valeur = valeur.replace('_CLE_NUM_CNPS_', ('%1s' % str(cle_cnps))[:1])
            valeur = valeur.replace('_MATRICULE_', ("%14s" % matricule)[:14])
            try:
                nomprenom = unicodedata.normalize('NFKD', unicode(nomprenom))
                valeur = valeur.replace('_NOMPRENOM_', (u"%60s" % nomprenom.encode('ascii', 'ignore'))[:60])
            except UnicodeDecodeError:
                valeur = valeur.replace('_NOMPRENOM_', "----------")
            valeur = valeur.replace('ANNEE_DIPES', ("%04d" % self.annee)[:4])
            valeur = valeur.replace('NOMBRE_JOUR', ("%2s" % str(diffrence_jour))[:2])
            valeur = valeur.replace('MOIS', "%02d" % int(self.mois))
            valeur = valeur.replace('LIGNE', "%02d" % ligne_col)
            valeur = valeur.replace(
                'NUMERO_FEUILLET', "%02d" % (i / 16 + 1))
            valeur = valeur.replace(
                'SALAIRE_BRUT', "%0.10d" % int(round(salaire_brut)))
            valeur = valeur.replace(
                '_SALAIRE_EXCEPTIONNEL_', "%0.10d" % int(round(salaire_excep)))

            valeur = valeur.replace(
                'SALAIRE_TAXABLE',
                "%0.10d" % int(round(salaire_taxa)))

            valeur = valeur.replace(
                'SALAIRE_CNPS',
                "%0.10d" % int(round(salaire_cnps)))

            valeur = valeur.replace(
                'SALAIRE_PLAFONNE',
                "%0.10d" % int(round(salaire_plaf)))

            valeur = valeur.replace(
                '_IRPP_', "%0.8d" % int(round(irpp)))
            valeur = valeur.replace(
                '_TC_', "%0.6d" % int(round(taxe_comm)))
            valeur = valeur.replace('_', ' ')
            i += 1

            dipes.append(valeur)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'corpe_paie.dipes_mensuel.xls',
            'context': {'xls_export': 1, 'dipes': dipes},
            'datas': {}}
