# -*- coding: utf-8 -*-
from openerp import api, fields, models

DEFAULT_JOUR_SALAIRE = 1


class HrConfigSettings(models.Model):
    """."""

    _inherit = 'hr.config.settings'

    jour_paiement = fields.Integer(
        string="Jour de paiement salaire",
        help="Indiquez la date par defaut de paiement des salaires",
        default=DEFAULT_JOUR_SALAIRE)

    @api.multi
    def set_jour_paiement(self):
        self.ensure_one()

        value = getattr(self, "jour_paiement", DEFAULT_JOUR_SALAIRE)
        self.env['ir.config_parameter'].set_param("jour_paiement", value)

    def get_nombre_quart_jour(self, cr, uid, fields, context=None):
        res = {}
        res["jour_paiement"] = self.env['ir.config_parameter'].get_param(
            "jour_paiement", DEFAULT_JOUR_SALAIRE)
        return res