# -*- coding: utf-8 -*-
from openerp import api, fields, models


class IntervenantLine(models.Model):
	
	_name = "corpe_maintenance.intervenant_line"

	employee_id = fields.Many2one(
		string="Intervenant",
		comodel_name="hr.employee"
	)

	poste_intervenant = fields.Char(
		string="Titre du poste",
		compute="compute_poste",
		store=True
	)

	activite_id = fields.Many2one(
		comodel_name="corpe_maintenance.activite"
	)

	@api.depends('employee_id')
	def compute_poste(self):
		super_user = self.employee_id.sudo()

		if super_user.contract_id:
			if super_user.contract_id.job_id:
				self.poste_intervenant = super_user.contract_id.job_id.name
