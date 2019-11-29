# -*- coding: utf-8 -*-
from openerp import api, fields, models, _


class HrDepartment(models.Model):

    _inherit = 'hr.department'

    code_centre = fields.Char(string="Code")

    nom_centre = fields.Char(string='Nom du centre')

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account')
