# -*- coding: utf-8 -*-
from openerp import fields, models


class HrSalaryRule(models.Model):

    _inherit = 'hr.salary.rule'

    analytic_account_id = fields.Many2one(
        string="Compte analytique",
        comodel_name="account.analytic.account")

    is_analytic_account = fields.Boolean(
        string="Comptabilisation analytique ?",
        default=False)

    account_tax_id = fields.Many2one(
        string="Compte de taxe",
        comodel_name="account.tax.code")

    account_debit = fields.Many2one(
        string="Compte de debit",
        comodel_name="account.account")

    account_credit = fields.Many2one(
        string="Compte de credit",
        comodel_name="account.account")

    use_personal_account = fields.Selection(
        string="Utiliser les comptes personnels",
        selection=[
            ('no', 'Ne pas utiliser'),
            ('debit', 'Compte personnel en debit'),
            ('credit', 'Compte personnel en credit')],
        default="no",
        required=True)

    a_comptabiliser = fields.Boolean(
        string="A comptabiliser",
        default=True,
        help="""Cochez cette case pour indiquer """
             """si cette regle doit etre comptabilisee""")

    partner_rule = fields.Many2one(
        string="Partenaire de la regle",
        comodel_name="res.partner")
