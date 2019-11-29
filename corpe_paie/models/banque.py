from openerp import models, fields


# cette classe permet de configurer les banques
class EmployeeBanque(models.Model):

    _name = "corpe_paie.banque"

    name = fields.Char(string="Nom", required=True)

    code = fields.Char(string="Code", required=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Ce nom de banque existe deja'),
        ('code_unique', 'unique(code)', 'Ce code de banque existe deja')
    ]