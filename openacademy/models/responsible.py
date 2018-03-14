# -*-coding: utf-8 -*-
from openerp import models, fields, api


class Responsible(models.Model):
	_name='openacademy.responsible'

	name = fields.Char(string="Name", required=True)
	surname = fields.Char()
	grade = fields.Char()