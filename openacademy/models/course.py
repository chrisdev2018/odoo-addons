# -*-coding: utf-8 -*-
from openerp import models, fields, api


class Course(models.Model):
	_name='openacademy.course'

	name = fields.Char(string="Titre", required=True)

	responsible_id = fields.Many2one('openacademy.responsible',
									 ondelete='set null', string='Responsable',
									 index=True)

	description = fields.Text()
