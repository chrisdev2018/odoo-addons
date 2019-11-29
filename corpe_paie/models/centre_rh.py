# -*- coding: utf-8 -*-
from openerp import models, fields

class CentreRH(models.Model):
	_name = "corpe_paie.centre_rh"
	
	name = fields.Char(
		string="Nom",
		required=True
	)
	
	code = fields.Char(
		string="Code",
		required=True
	)
