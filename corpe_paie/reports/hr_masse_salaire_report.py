# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# report.hr.masse_salaire

from openerp import fields, models
from openerp import tools


class ReportHrMasseSalaire(models.Model):
    _name = "corpe_paie.report_hr_masse_salaire"
    _description = "Masse salariale"
    _order = 'slip_id'
    _auto = False

    slip_id = fields.Many2one(
        'hr.payslip',
        'Bulletin',
        readonly=True)

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        'Rule',
        readonly=True)

    category_id = fields.Many2one(
        'hr.salary.rule.category',
        'Categorie',
        readonly=True)

    name_related = fields.Char(string="Nom & prenom")

    employee_id = fields.Many2one(
        'hr.employee',
        'Employe',
        readonly=True)

    amount = fields.Float(
        'Montant',
        readonly=True)

    quantity = fields.Float(
        'Quantite',
        readonly=True)

    total = fields.Float(
        'Total',
        readonly=True)

    contract_id = fields.Many2one(
        'hr.contract',
        'Contrat',
        readonly=True)

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE or REPLACE view corpe_paie_report_hr_masse_salaire as

                SELECT ts.id,
                    he.identification_id,
                    he.otherid,
                    he.name_related,
                    he.birthday,
                    he.job_id,
                    ts.salary_rule_id,
                    ts.employee_id as employee_id,
                    ts.slip_id,
                    ts.total

                FROM hr_payslip_line ts
                    JOIN hr_payslip hp ON hp.id = ts.slip_id
                    LEFT JOIN hr_salary_rule_category hc ON hc.id = ts.category_id
                    LEFT JOIN hr_salary_rule hr ON hr.id = ts.salary_rule_id
                    LEFT JOIN hr_employee he ON he.id = ts.employee_id

                GROUP BY
                    ts.id,
                    ts.salary_rule_id,
                    ts.employee_id,
                    ts.category_id,
                    ts.total,
                    he.name_related,
                    he.identification_id,
                    he.otherid,
                    he.birthday,
                    he.job_id;

        """)
