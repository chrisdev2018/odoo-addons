# -*- coding: utf-8 -*-
from openerp import api, fields, models
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
	_inherit = 'hr.payslip'
	
	base = fields.Float(
		string="Salaire de base",
		compute="_depends_contract",
		readonly=False
	)
	
	base_indiciel = fields.Float(
		string="Salaire de base indiciel",
		compute="_depends_contract",
		readonly=False
	)
	
	grille_salariale = fields.Many2one(
		string="Grille salaire",
		comodel_name="corpe_paie.grille_salaire",
		compute="_depends_contract",
		readonly=False
	)
	
	date_paiement = fields.Date(
		string="Date de paiement",
		readonly=True,
		states={'draft': [('readonly', False)]})
	
	nb_jours = fields.Integer(
		string="Nombre de Jours",
		compute="_nb_jours")
	
	anciennete = fields.Char(
		string="Ancienneté",
		compute="_depends_contract"
	)
	
	annee_anciennete = fields.Integer(
		string="Anciennete en annee",
		compute="_depends_contract",
	)
	
	@api.depends('contract_id')
	def _depends_contract(self):
		for rec in self:
			#recupere la grille salaire
			rec.grille_salariale = rec.contract_id.grille_salaire.id
			
			#recupere le salaire de base
			rec.base = rec.contract_id.wage
			
			#recupere le salaire de base indiciel
			rec.base_indiciel = rec.contract_id.base_indice
			
			#calcul et affecte l'anciennete
			rec.anciennete = ""
			rec.annee_anciennete = 0
			date_start = rec.contract_id.date_start
			
			if date_start and len(date_start) > 9:
				object_date_start = datetime.strptime(date_start[:10], "%Y-%m-%d")
				object_date_start = object_date_start.replace(day=1)
				fin_mois = datetime.strptime(rec.date_to[:10], "%Y-%m-%d")
				fin_mois += relativedelta(days=1)
				diff = relativedelta(fin_mois, object_date_start)
				rec.anciennete += str(diff.years)
				rec.anciennete += " an(s) " if diff.years > 1 else " an"
				rec.anciennete += " %s mois" % str(diff.months)
				
				rec.annee_anciennete = diff.years
	
	@api.multi
	def _nb_jours(self):
		for bull in self:
			if bull.date_from:
				_date = datetime.strptime(bull.date_from, '%Y-%m-%d')
				bull.nb_jours = monthrange(_date.year, _date.month)[1]
			else:
				bull.nb_jours = 0
	
	@api.constrains('contract_id')
	def check_date_paiement(self):
		for record in self:
			if not record.date_paiement:
				jour_paye = self.env['ir.config_parameter'].get_param(
					"jour_paiement", 1)
				maintenant = datetime.now()
				date = "%s-%.2d-%.2d" % (
					maintenant.year, maintenant.month, int(jour_paye))
				lot_bull = record.payslip_run_id
				if lot_bull and lot_bull.date_paiement:
					date = lot_bull.date_paiement
				elif record.date_from:
					date = record.date_from[:8] + "%.2d" % int(jour_paye)
				record.date_paiement = date
	
	@api.constrains('contract_id')
	def _check_primes(self):
		for r in self:
			r.input_line_ids.unlink()
			if r.contract_id:
				i = 1
				for prime_ind in r.contract_id.primes_ind:
					r.write({'input_line_ids': [[
						0, False, {
							'name': prime_ind.regle_salariale.name,
							'code': prime_ind.code,
							'amount': prime_ind.montant,
							'contract_id': prime_ind.contrat_id.id,
							'sequence': i}]]})
					i += 1
