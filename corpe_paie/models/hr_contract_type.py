# -*- coding: utf-8 -*-
from openerp import fields, models


class HrContractType(models.Model):

    _inherit = 'hr.contract.type'

    grilles_salaire = fields.Many2many(
        string='Grilles de ce type de contrat',
        readonly=False,
        required=False,
        help="grilles prises en charge par ce type de contrat",
        comodel_name='corpe_paie.grille_salaire',
        relation='model_grille_to_typecontrat')
