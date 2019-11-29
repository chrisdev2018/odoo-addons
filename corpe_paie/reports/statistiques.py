# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import xlwt
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'move.line.list.xls'

FIELD_TEXT = "line.{} if hasattr(line, '{}') else ''"
FIELD_NUMBER = "line.{} if hasattr(line, '{}') else 0"
FIELD_DATE = "line.{} if hasattr(line, '{}') else ''"
NO_PAYSLIP_FOUND = _("Aucun bulletin de paie dans la periode")


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class StatistiquesParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(StatistiquesParser, self).__init__(
            cr, uid, name, context=context)
        payslip_line_obj = self.pool.get('account.move.line')
        self.context = context

        wanted_list = context['colonnes'] or []
        template_changes = {}
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'title': context['title'] or "Fichier excel",
            'debut': context['debut'] or "",
            'fin': context['fin'] or "",
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src


class StatistiquesXls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(StatistiquesXls, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {
            'move': {
                'header': [1, 20, 'text', _render("_('Entry')")],
                'lines': [1, 0, 'text', _render("line.move_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'name': {
                'header': [1, 42, 'text', _render("_('Nom')")],
                'lines': [1, 0, 'text', _render("line.name or ''")],
                'totals': [1, 0, 'text', None]},
            'prenom': {
                'header': [1, 42, 'text', _render("_('Prenom')")],
                'lines': [1, 0, 'text', _render("line.prenom or ''")],
                'totals': [1, 0, 'text', None]},
            'birthday': {
                'header': [1, 42, 'text', _render("_('Date de naissance')")],
                'lines': [1, 0, 'text', _render("line.birthday or ''")],
                'totals': [1, 0, 'text', None]},
            'base': {
                'header': [1, 42, 'text', _render("_('SALBASE')")],
                'lines': [1, 0, 'number', _render("line.base or ''")],
                'totals': [1, 0, 'text', None]},
            'sb': {
                'header': [1, 42, 'text', _render("_('Salaire brut')")],
                'lines': [1, 0, 'number', _render("line.sb or ''")],
                'totals': [1, 0, 'text', None]},
            'sbt': {
                'header': [1, 42, 'text', _render("_('Salaire taxable')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'sbt'))],
                'totals': [1, 0, 'text', None]},
            'sc': {
                'header': [1, 42, 'text', _render("_('Salaire Cotisable')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'sc'))],
                'totals': [1, 0, 'text', None]},
            'irpp': {
                'header': [1, 42, 'text', _render("_('IRPP')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'irpp'))],
                'totals': [1, 0, 'text', None]},
            'nap': {
                'header': [1, 42, 'text', _render("_('NAP')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'nap'))],
                'totals': [1, 0, 'text', None]},
            'date': {
                'header': [1, 13, 'text', _render("_('Effective Date')")],
                'lines': [1, 0, 'date',
                          _render("datetime.strptime(line.date,'%Y-%m-%d')"),
                          None, self.aml_cell_style_date],
                'totals': [1, 0, 'text', None]},
            'non_travail': {
                'header': [1, 12, 'text', _render("_('Periode non travaillee')")],
                'lines':
                [1, 0, 'number',
                 _render(FIELD_NUMBER.replace('{}', 'non_travail'))],
                'totals': [1, 0, 'text', None]},
            'anciennete': {
                'header': [1, 36, 'text', _render("_('Anciennete')")],
                'lines':
                [1, 0, 'number',
                 _render("line.anciennete if hasattr(line, 'anciennete') else 0")],
                'totals': [1, 0, 'text', None]},
            'transport': {
                'header': [1, 36, 'text', _render("_('Transport')")],
                'lines':
                [1, 0, 'number',
                 _render(FIELD_NUMBER.replace('{}', 'transport'))],
                'totals': [1, 0, 'text', None]},
            'hs20': {
                'header': [1, 12, 'text', _render("_('HS 20%')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'hs20'))],
                'totals': [1, 0, 'text', None]},
            'hs30': {
                'header': [1, 13, 'text', _render("_('HS 30%')")],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'hs30'))],
                'totals': [1, 0, 'text', None]},
            'hs40': {
                'header': [1, 18, 'text', _render("_('HS 40%')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'hs40'))],
                'totals': [1, 0, 'number', None]},
            'hs50': {
                'header': [1, 18, 'text', _render("_('HS 50%')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'hs50'))],
                'totals': [1, 0, 'number', None]},
            'logement': {
                'header': [1, 18, 'text', _render("_('Logement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'logement'))],
                'totals': [1, 0, 'number', None]},
            'nuit': {
                'header': [1, 18, 'text', _render("_('Panier')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'nuit'))],
                'totals': [1, 0, 'number', None]},
            'responsabilite': {
                'header': [1, 18, 'text', _render("_('Responsabilite')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'responsabilite'))],
                'totals': [1, 0, 'number', None]},
            'medaille': {
                'header': [1, 18, 'text', _render("_('Prime de Médaille')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'medaille'))],
                'totals': [1, 0, 'number', None]},
            'separation': {
                'header': [1, 18, 'text', _render("_('Prime de bnonne Séparation')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'separation'))],
                'totals': [1, 0, 'number', None]},
            'assiduite': {
                'header': [1, 18, 'text', _render("_(u'Assiduité')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'assiduite'))],
                'totals': [1, 0, 'number', None]},
            'technicite': {
                'header': [1, 18, 'text', _render("_(u'Technicité')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'technicite'))],
                'totals': [1, 0, 'number', None]},
            'rendement': {
                'header': [1, 18, 'text', _render("_('Rendement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'rendement'))],
                'totals': [1, 0, 'number', None]},
            'representation': {
                'header': [1, 18, 'text', _render("_('Representation')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'representation'))],
                'totals': [1, 0, 'number', None]},
            'remplacement': {
                'header': [1, 18, 'text', _render("_('Remplacement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'remplacement'))],
                'totals': [1, 0, 'number', None]},
            'vente': {
                'header': [1, 18, 'text', _render("_('Prime de vente')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'vente'))],
                'totals': [1, 0, 'number', None]},
            'conges': {
                'header': [1, 18, 'text', _render("_('Congés')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'conges'))],
                'totals': [1, 0, 'number', None]},
            'voiture': {
                'header': [1, 18, 'text', _render("_('Vehicule')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'voiture'))],
                'totals': [1, 0, 'number', None]},
            'sit': {
                'header': [1, 18, 'text', _render("_('Base Taxable')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'sit'))],
                'totals': [1, 0, 'number', None]},
            'loge_tax': {
                'header': [1, 18, 'text', _render("_('Logement imposable')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'loge_tax'))],
                'totals': [1, 0, 'number', None]},
            'voiture_tax': {
                'header': [1, 18, 'text', _render("_('Voiture Taxable')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'voiture_tax'))],
                'totals': [1, 0, 'number', None]},
            'licenciement': {
                'header': [1, 18, 'text', _render("_('Licenciement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'licenciement'))],
                'totals': [1, 0, 'number', None]},
            'preavis': {
                'header': [1, 18, 'text', _render("_('Preavis')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'preavis'))],
                'totals': [1, 0, 'number', None]},
            'deces': {
                'header': [1, 18, 'text', _render("_('Indemnite de deces')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'deces'))],
                'totals': [1, 0, 'number', None]},
            'sb': {
                'header': [1, 18, 'text', _render("_('Brut')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'sb'))],
                'totals': [1, 0, 'number', None]},
            'mutuelle': {
                'header': [1, 18, 'text', _render("_('Mutuelle')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'mutuelle'))],
                'totals': [1, 0, 'number', None]},
            'cac_irpp': {
                'header': [1, 18, 'text', _render("_('CAC/IRPP')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'cac_irpp'))],
                'totals': [1, 0, 'number', None]},
            'tdl': {
                'header': [1, 18, 'text', _render("_('TDL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'tdl'))],
                'totals': [1, 0, 'number', None]},
            'cfp': {
                'header': [1, 18, 'text', _render("_('CF PATRONAL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'cfp'))],
                'totals': [1, 0, 'number', None]},
            'assurance': {
                'header': [1, 18, 'text', _render("_('ASSUR Maladie')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'assurance'))],
                'totals': [1, 0, 'number', None]},
            'assur_auto': {
                'header': [1, 18, 'text', _render("_('ASSUR AUTO')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'assur_auto'))],
                'totals': [1, 0, 'number', None]},
            'credit_com': {
                'header': [1, 18, 'text', _render("_('Crédit Tel.')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'credit_com'))],
                'totals': [1, 0, 'number', None]},
            'cfs': {
                'header': [1, 18, 'text', _render("_('CF SALARIAL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'cfs'))],
                'totals': [1, 0, 'number', None]},
            'sursalaire': {
                'header': [1, 18, 'text', _render("_('Sursalaire')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'sursalaire'))],
                'totals': [1, 0, 'number', None]},
            'rappel_salaire': {
                'header': [1, 18, 'text', _render("_('Rappel sur Salaire')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'rappel_salaire'))],
                'totals': [1, 0, 'number', None]},
            'rav': {
                'header': [1, 18, 'text', _render("_('RAV')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'rav'))],
                'totals': [1, 0, 'number', None]},
            'syndicat': {
                'header': [1, 18, 'text', _render("_('Syndicat')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'syndicat'))],
                'totals': [1, 0, 'number', None]},
            'pret': {
                'header': [1, 18, 'text', _render("_('Pret entreprise')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'pret'))],
                'totals': [1, 0, 'number', None]},
            'retenues_diverses': {
                'header': [1, 18, 'text', _render("_('Retenues Diverses')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'retenues_diverses'))],
                'totals': [1, 0, 'number', None]},
            'pf': {
                'header': [1, 18, 'text', _render("_('All. Fam.')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'pf'))],
                'totals': [1, 0, 'number', None]},
            'pvid_pat': {
                'header': [1, 18, 'text', _render("_('PV PATRONAL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'pvid_pat'))],
                'totals': [1, 0, 'number', None]},
            'pvid_sal': {
                'header': [1, 18, 'text', _render("_('PV SALARIAL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'pvid_sal'))],
                'totals': [1, 0, 'number', None]},
            'rp': {
                'header': [1, 18, 'text', _render("_('A. T.')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'rp'))],
                'totals': [1, 0, 'number', None]},
            'fne': {
                'header': [1, 18, 'text', _render("_('FNE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'fne'))],
                'totals': [1, 0, 'number', None]},
            'date_sortie': {
                'header': [1, 18, 'text', _render("_('Date de sortie')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'date_sortie'))],
                'totals': [1, 0, 'number', None]},
            'date_embauche': {
                'header': [1, 18, 'text', _render("_('Date embauche')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'date_embauche'))],
                'totals': [1, 0, 'number', None]},
            'poste': {
                'header': [1, 18, 'text', _render("_(u'Emploi occupé')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'poste'))],
                'totals': [1, 0, 'number', None]},
            'coefficient': {
                'header': [1, 18, 'text', _render("_('Coefficient')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'coefficient'))],
                'totals': [1, 0, 'number', None]},
            'niveau': {
                'header': [1, 18, 'text', _render("_('Niveau')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'niveau'))],
                'totals': [1, 0, 'number', None]},
            'categorie': {
                'header': [1, 18, 'text', _render("_('Catégorie')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'categorie'))],
                'totals': [1, 0, 'number', None]},
            'civilite': {
                'header': [1, 18, 'text', _render("_('Civilité')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'civilite'))],
                'totals': [1, 0, 'number', None]},
            'identification_id': {
                'header': [1, 18, 'text', _render("_('Matricule')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'identification_id'))],
                'totals': [1, 0, 'number', None]},
            'otherid': {
                'header': [1, 18, 'text', _render("_('Numéro de Sécurité Sociale')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'otherid'))],
                'totals': [1, 0, 'number', None]},
            'methode_paiement': {
                'header': [1, 18, 'text', _render("_('Mode de paiement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'methode_paiement'))],
                'totals': [1, 0, 'number', None]},
            'cle_cnps': {
                'header': [1, 18, 'text', _render("_('Clé du numéro de Sécurité Sociale')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'cle_cnps'))],
                'totals': [1, 0, 'number', None]},
            'code_centre': {
                'header': [1, 18, 'text', _render("_('Code établissement')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'code_centre'))],
                'totals': [1, 0, 'number', None]},
            'banque_nom': {
                'header': [1, 18, 'text', _render("_('Nom banque 1')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'banque_nom'))],
                'totals': [1, 0, 'number', None]},
            'banque_code': {
                'header': [1, 18, 'text', _render("_('Code banque 1')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'banque_code'))],
                'totals': [1, 0, 'number', None]},
            'num_compte': {
                'header': [1, 18, 'text', _render("_('Numéro de compte 1')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'num_compte'))],
                'totals': [1, 0, 'number', None]},
            'code_guichet': {
                'header': [1, 18, 'text', _render("_('Code guichet 1')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'code_guichet'))],
                'totals': [1, 0, 'number', None]},
            'cle_rib': {
                'header': [1, 18, 'text', _render("_('Clé RIB 1')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'cle_rib'))],
                'totals': [1, 0, 'number', None]},
            'matricule': {
                'header': [1, 18, 'text', _render("_('Matricule')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'matricule'))],
                'totals': [1, 0, 'number', None]},
            'mat_cnps': {
                'header': [1, 18, 'text', _render("_('Numéro de Sécurité Sociale')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'mat_cnps'))],
                'totals': [1, 0, 'number', None]},
            'numero_dipe': {
                'header': [1, 18, 'text', _render("_('NUMERO DIPE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'numero_dipe'))],
                'totals': [1, 0, 'number', None]},
            'cle_numero_dipe': {
                'header': [1, 18, 'text', _render("_('CLE NUMERO DIPE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'cle_numero_dipe'))],
                'totals': [1, 0, 'number', None]},
            'avances': {
                'header': [1, 18, 'text', _render("_('Acomptes')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_TEXT.replace('{}', 'avances'))],
                'totals': [1, 0, 'number', None]},
            'acompte_non_retenus': {
                'header': [1, 18, 'text', _render("_('Acomptes non retenus')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_TEXT.replace('{}', 'acompte_non_retenus'))],
                'totals': [1, 0, 'number', None]},
            'numero_contribuable': {
                'header': [1, 18, 'text', _render("_('NUMERO CONTRIBUABLE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'numero_contribuable'))],
                'totals': [1, 0, 'number', None]},
            'numero_employeur': {
                'header': [1, 18, 'text', _render("_('NUMERO EMPLOYEUR')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'numero_employeur'))],
                'totals': [1, 0, 'number', None]},
            'cle_numero_employeur': {
                'header': [1, 18, 'text', _render("_('CLE NUMERO EMPLOYEUR')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'cle_numero_employeur'))],
                'totals': [1, 0, 'number', None]},
            'regime_employeur': {
                'header': [1, 18, 'text', _render("_('REGIME EMPLOYEUR')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'regime_employeur'))],
                'totals': [1, 0, 'number', None]},
            'annee': {
                'header': [1, 18, 'text', _render("_('ANNEE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_NUMBER.replace('{}', 'annee'))],
                'totals': [1, 0, 'number', None]},
            'mois': {
                'header': [1, 18, 'text', _render("_('MOIS')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_NUMBER.replace('{}', 'mois'))],
                'totals': [1, 0, 'number', None]},
            'jour': {
                'header': [1, 18, 'text', _render("_('NOMBRE DE JOURS')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'jour'))],
                'totals': [1, 0, 'number', None]},
            'code_enregistrement': {
                'header': [1, 18, 'text', _render("_('CODE ENREGISTREMENT')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render(FIELD_TEXT.replace('{}', 'code_enregistrement'))],
                'totals': [1, 0, 'number', None]},
            'salex': {
                'header': [1, 18, 'text', _render("_('SALAIRE EXCEPTIONNEL')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'salex'))],
                'totals': [1, 0, 'number', None]},
            'fin_carriere': {
                'header': [1, 18, 'text', _render("_('FIN DE CARRIERE')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render(FIELD_NUMBER.replace('{}', 'fin_carriere'))],
                'totals': [1, 0, 'number', None]},

            # 'credit': {
            #     'header': [1, 18, 'text', _render("_('Credit')"), None,
            #                self.rh_cell_style_right],
            #     'lines': [1, 0, 'number', _render("line.credit"), None,
            #               self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'number', None, _render("credit_formula"),
            #                self.rt_cell_style_decimal]},
            # 'balance': {
            #     'header': [1, 18, 'text', _render("_('Balance')"), None,
            #                self.rh_cell_style_right],
            #     'lines': [1, 0, 'number', None, _render("bal_formula"),
            #               self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'number', None, _render("bal_formula"),
            #                self.rt_cell_style_decimal]},
            # 'reconcile': {
            #     'header': [1, 12, 'text', _render("_('Rec.')"), None,
            #                self.rh_cell_style_center],
            #     'lines': [1, 0, 'text',
            #               _render("line.reconcile_id.name or ''"), None,
            #               self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
            # 'reconcile_partial': {
            #     'header': [1, 12, 'text', _render("_('Part. Rec.')"), None,
            #                self.rh_cell_style_center],
            #     'lines': [1, 0, 'text',
            #               _render("line.reconcile_partial_id.name or ''"),
            #               None, self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
            # 'tax_code': {
            #     'header': [1, 12, 'text', _render("_('Tax Code')"), None,
            #                self.rh_cell_style_center],
            #     'lines': [1, 0, 'text', _render("line.tax_code_id.code or ''"),
            #               None, self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
            # 'tax_amount': {
            #     'header': [1, 18, 'text', _render("_('Tax/Base Amount')"),
            #                None, self.rh_cell_style_right],
            #     'lines': [1, 0, 'number', _render("line.tax_amount"), None,
            #               self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'text', None]},
            # 'amount_currency': {
            #     'header': [1, 18, 'text', _render("_('Am. Currency')"), None,
            #                self.rh_cell_style_right],
            #     'lines':
            #     [1, 0,
            #      _render("line.amount_currency and 'number' or 'text'"),
            #      _render("line.amount_currency or None"),
            #      None, self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'text', None]},
            # 'currency_name': {
            #     'header': [1, 6, 'text', _render("_('Curr.')"), None,
            #                self.rh_cell_style_center],
            #     'lines':
            #     [1, 0, 'text',
            #      _render("line.currency_id and line.currency_id.name or ''"),
            #      None, self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
            # 'journal': {
            #     'header': [1, 12, 'text', _render("_('Journal')")],
            #     'lines': [1, 0, 'text', _render("line.journal_id.code or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'company_currency': {
            #     'header': [1, 10, 'text', _render("_('Comp. Curr.')")],
            #     'lines': [1, 0, 'text',
            #               _render("line.company_id.currency_id.name or ''"),
            #               None, self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
            # 'analytic_account': {
            #     'header': [1, 36, 'text', _render("_('Analytic Account')")],
            #     'lines': [1, 0, 'text',
            #               _render("line.analytic_account_id.code or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'product': {
            #     'header': [1, 36, 'text', _render("_('Product')")],
            #     'lines': [1, 0, 'text', _render("line.product_id.name or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'product_ref': {
            #     'header': [1, 36, 'text', _render("_('Product Reference')")],
            #     'lines': [1, 0, 'text',
            #               _render("line.product_id.default_code or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'product_uom': {
            #     'header': [1, 20, 'text', _render("_('Unit of Measure')")],
            #     'lines': [1, 0, 'text',
            #               _render("line.product_uom_id.name or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'quantity': {
            #     'header': [1, 8, 'text', _render("_('Qty')"), None,
            #                self.rh_cell_style_right],
            #     'lines': [1, 0,
            #               _render("line.quantity and 'number' or 'text'"),
            #               _render("line.quantity or None"), None,
            #               self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'text', None]},
            # 'statement': {
            #     'header': [1, 20, 'text', _render("_('Statement')")],
            #     'lines':
            #     [1, 0, 'text',
            #      _render("line.statement_id and line.statement_id.name or ''")
            #      ],
            #     'totals': [1, 0, 'text', None]},
            # 'invoice': {
            #     'header': [1, 20, 'text', _render("_('Invoice')")],
            #     'lines':
            #     [1, 0, 'text',
            #      _render("line.invoice and line.invoice.number or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'amount_residual': {
            #     'header': [1, 18, 'text', _render("_('Residual Amount')"),
            #                None, self.rh_cell_style_right],
            #     'lines':
            #     [1, 0,
            #      _render("line.amount_residual and 'number' or 'text'"),
            #      _render("line.amount_residual or None"),
            #      None, self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'text', None]},
            # 'amount_residual_currency': {
            #     'header': [1, 18, 'text', _render("_('Res. Am. in Curr.')"),
            #                None, self.rh_cell_style_right],
            #     'lines':
            #     [1, 0,
            #      _render(
            #          "line.amount_residual_currency and 'number' or 'text'"),
            #      _render("line.amount_residual_currency or None"),
            #      None, self.aml_cell_style_decimal],
            #     'totals': [1, 0, 'text', None]},
            # 'narration': {
            #     'header': [1, 42, 'text', _render("_('Notes')")],
            #     'lines': [1, 0, 'text',
            #               _render("line.move_id.narration or ''")],
            #     'totals': [1, 0, 'text', None]},
            # 'blocked': {
            #     'header': [1, 4, 'text', _('Lit.'),
            #                None, self.rh_cell_style_right],
            #     'lines': [1, 0, 'text', _render("line.blocked and 'x' or ''"),
            #               None, self.aml_cell_style_center],
            #     'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        # recupere la societe
        company_obj = self.pool.get('res.company')
        ste_id = company_obj.search(self.cr, self.uid, [], limit=1)
        ste = company_obj.browse(self.cr, self.uid, ste_id)

        # les traitements
        payslip_line_obj = self.pool.get('hr.payslip.line')
        domain = []
        if _p.debut and _p.fin:
            domain.append(('slip_id.date_from', '>=', _p.debut))
            domain.append(('slip_id.date_to', '<=', _p.fin))
        all_ids = payslip_line_obj.search(self.cr, self.uid, domain)
        if not all_ids:
            raise Warning(NO_PAYSLIP_FOUND)
        all_objs = payslip_line_obj.browse(self.cr, self.uid, all_ids)

        result = []
        for employee in all_objs.mapped('employee_id'):
            contract = employee.contract_id
            department = employee.department_id
            banque = employee.banque_id

            obbj = {}
            obbj['name'] = employee.name_related or ""
            obbj['prenom'] = employee.prenom or ""
            
            birthday = employee.birthday if employee.birthday else ""
            format_birthday = datetime.strptime(birthday, "%Y-%m-%d") if birthday != "" else ""
            
            obbj['birthday'] = format_birthday.strftime("%d-%m-%Y") if format_birthday != "" else ""
            obbj['cle_cnps'] = str(employee.cle_cnps or "")
            obbj['civilite'] = "Monsieur" if employee.gender == 'male' else "Madame"
            obbj['identification_id'] = (employee.identification_id or "")
            obbj['num_compte'] = str(employee.num_compte or "")
            obbj['code_guichet'] = str(employee.code_guichet or "")
            obbj['cle_rib'] = str(employee.cle_rib or "")
            obbj['otherid'] = str(employee.otherid or "")
            obbj['mat_cnps'] = str(employee.mat_cnps or "")
            obbj['poste'] = (employee.job_id.name or "") if employee.job_id else ""

            obbj['code_centre'] = employee.centre_rh_id.code if employee.centre_rh_id else "xxxxxx"
            
            debut = contract.date_start if contract.date_start else ""
            fin = contract.date_end if contract.date_end else ""
            
            format_debut = datetime.strptime(debut, "%Y-%m-%d") if debut != "" else ""
            format_fin = datetime.strptime(fin, "%Y-%m-%d") if fin != "" else ""
            
            obbj['date_sortie'] = (format_fin.strftime("%d-%m-%Y") if format_fin != "" else "") if contract\
                else ""
            obbj['date_embauche'] = (format_debut.strftime("%d-%m-%Y") if format_debut != "" else "") if contract\
                else ""
            obbj['categorie'] = (contract.categorie or "") if contract else ""
            obbj['methode_paiement'] = contract.methode_paiement if contract else ""
            obbj['matricule'] = (contract.name or "") if contract else ""

            obbj['banque_nom'] = str(banque.name or "") if banque else ""
            obbj['banque_code'] = str(banque.code or "") if banque else ""

            obbj['numero_dipe'] = str(ste.numero_dipe or "")
            obbj['cle_numero_dipe'] = str(ste.cle_numero_dipe or "")
            obbj['numero_contribuable'] = str(ste.numero_contribuable or "")
            obbj['numero_employeur'] = str(ste.numero_employeur or "")
            obbj['cle_numero_employeur'] = str(ste.cle_numero_employeur or "")
            obbj['regime_employeur'] = str(ste.regime_employeur or "")
            obbj['annee'] = _p.fin[:4]
            obbj['mois'] = _p.fin[5:7]

            obbj['code_enregistrement'] = "C04"
            
            # On recupere le premier bulletin du mois en cours de l'employe
            # Et on y recupere la grille salariale
            all_bull = all_objs.filtered(
                lambda x: x.employee_id.id == employee.id).mapped('slip_id')
            first_bull = all_bull[0]
            grille_salaire = first_bull.grille_salariale
            
            if grille_salaire:
                obbj['coefficient'] = grille_salaire.ech_id.code
                obbj['niveau'] = grille_salaire.categ_id.code

            all_objs_emp = all_objs.filtered(
                lambda x: x.employee_id.id == employee.id)
            for ligne in all_objs_emp:
                key = ligne.code.lower().replace("/", "_")
                if key in obbj.keys():
                    obbj[key] += ligne.total
                else:
                    obbj[key] = ligne.total
            result.append(Struct(**obbj))
        objects = result

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._

        debit_pos = 'debit' in wanted_list and wanted_list.index('debit')
        credit_pos = 'credit' in wanted_list and wanted_list.index('credit')
        if not (credit_pos and debit_pos) and 'balance' in wanted_list:
            raise orm.except_orm(
                _('Customisation Error!'),
                _("The 'Balance' field is a calculated XLS field requiring \
                the presence of the 'Debit' and 'Credit' fields !"))

        # report_name = objects[0]._description or objects[0]._name
        report_name = _p.title or _("Statistique Paie")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        row_pos += 1

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_template, 'header', render_space={'_': _p._}),
            wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        # account move lines
        for line in objects:
            debit_cell = rowcol_to_cell(row_pos, debit_pos)
            credit_cell = rowcol_to_cell(row_pos, credit_pos)
            bal_formula = debit_cell + '-' + credit_cell
            _logger.debug('dummy call - %s', bal_formula)
            c_specs = map(
                lambda x: self.render(x, self.col_specs_template, 'lines'),
                wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

        # Totals
        # aml_cnt = len(objects)
        # debit_start = rowcol_to_cell(row_pos - aml_cnt, debit_pos)
        # debit_stop = rowcol_to_cell(row_pos - 1, debit_pos)
        # debit_formula = 'SUM(%s:%s)' % (debit_start, debit_stop)
        # _logger.debug('dummy call - %s', debit_formula)
        # credit_start = rowcol_to_cell(row_pos - aml_cnt, credit_pos)
        # credit_stop = rowcol_to_cell(row_pos - 1, credit_pos)
        # credit_formula = 'SUM(%s:%s)' % (credit_start, credit_stop)
        # _logger.debug('dummy call - %s', credit_formula)
        # debit_cell = rowcol_to_cell(row_pos, debit_pos)
        # credit_cell = rowcol_to_cell(row_pos, credit_pos)
        # bal_formula = debit_cell + '-' + credit_cell
        # _logger.debug('dummy call - %s', bal_formula)
        # c_specs = map(
        #     lambda x: self.render(x, self.col_specs_template, 'totals'),
        #     wanted_list)
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(
        #     ws, row_pos, row_data, row_style=self.rt_cell_style_right)


StatistiquesXls(
    'report.corpe_paie.statistiques_wizard.xls',
    'hr.payslip.line',
    parser=StatistiquesParser)
