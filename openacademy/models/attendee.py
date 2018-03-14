# -*-coding: utf-8 -*-
from openerp import models, fields, api


class Attendee(models.Model):
	_name='openacademy.attendee'

	name = fields.Char(string="Nom", required=True)
	