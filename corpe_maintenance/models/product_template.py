# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ProductProduct(models.Model):

	_inherit = "product.template"

	est_piece_rechange = fields.Boolean(
		string="Est une piece de rechange ? ",
		default=False
	)