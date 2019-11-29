# -*- coding: utf-8 -*-
from openerp import api, fields, models


class GrilleSalaire(models.Model):

    _inherit = ['mail.thread']
    _name = 'corpe_paie.grille_salaire'
    _description = 'Grille salariale'
    _rec_name = "code"
    _order = "num_ordre asc"

    name = fields.Char(string="Description", required=True)

    types_contrat = fields.Many2many(
        string='Type de contrat de cette grille',
        required=True,
        help="type de contrat prenant en charge cette grille",
        comodel_name='hr.contract.type',
        relation='model_grille_to_typecontrat')

    code = fields.Char(string="Code", required=True)

    montant = fields.Float(
        string="Salaire",
        required=True,
        digits=(16, 2))

    num_ordre = fields.Integer(
        string="Numero d'ordre",
        required=True)

    categ_id = fields.Many2one(
        comodel_name='corpe_paie.categorie_salariale',
        string="Categorie salariale")

    ech_id = fields.Many2one(
        comodel_name='corpe_paie.echelon_salariale',
        string="Echellon")

    contracts = fields.One2many(
        string='contracts',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help="contrats dans cette grille",
        comodel_name='hr.contract',
        inverse_name='grille_salaire')

    masse = fields.Float(
        string='Masse de la grille',
        readonly=True)

    @api.onchange('categ_id', 'ech_id')
    def onchange_num_ordre(self):
        if self.categ_id and self.ech_id:
            self.code = str(self.categ_id.code + self.ech_id.code).upper()
            self.num_ordre = self.categ_id.num_ordre * 20
            self.num_ordre += self.ech_id.num_ordre

    @api.constrains("montant")
    def update_salaries_employee(self):
        contract_obj = self.env["hr.contract"]
        for record in self:
            contracts = contract_obj.search([('grille_salaire', '!=', False)])
            contracts.update_salary()

    @api.constrains('montant', "contracts")
    def check_masse(self):
        self.update_masse()

    @api.multi
    def update_masse(self):
        for record in self:
            record.masse = sum(record.contracts.mapped('wage'))
