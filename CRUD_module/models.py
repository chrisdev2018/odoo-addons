# -*- coding: utf-8 -*-

from openerp import models, fields, api

class module_test(models.Model):
    _name = 'module_test.module_test'
    name = fields.Char()