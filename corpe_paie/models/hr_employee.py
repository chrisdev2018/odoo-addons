from openerp import models, fields


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    mat_cnps = fields.Char(
        string='Matricule CNPS',
        required=False
    )

    prenom = fields.Char(
        string='Prenom',
        required=False
    )

    cle_cnps = fields.Integer(
        string='Cle CNPS',
        required=False
    )

    cni = fields.Char(
        string='Numero CNI',
        required=False
    )

    num_compte = fields.Char(
        string='Numero de compte',
        required=False
    )

    code_guichet = fields.Char(
        string='Code guichet',
        required=False
        )
    cle_rib = fields.Char(
        string='Cle RIB',
        required=False
         )

    banque_id = fields.Many2one(
        string='Banque',
        readonly=False,
        required=False,
        help="Banque",
        comodel_name='corpe_paie.banque',
        )
    
    centre_rh_id = fields.Many2one(
        string="Centre/Etablissement",
        comodel_name="corpe_paie.centre_rh"
    )

    _sql_constraints = [
        ('cnps_unique', 'unique(mat_cnps)', 'Ce matricule CNPS existe deja'),
        ('contrainte_unique', 'unique(num_compte, banque_id)', 'la paire Banque-Numero de compte doit etre unique')
    ]
