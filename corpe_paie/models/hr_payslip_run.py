# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime
from openerp.tools import float_compare, float_is_zero
from openerp.exceptions import Warning


class HrPayslipRun(models.Model):

    _inherit = 'hr.payslip.run'

    date_paiement = fields.Date(
        string="Date de paiement",
        readonly=True,
        states={'draft': [('readonly', False)]})

    move = fields.Many2one(
        string="Piece comptable",
        comodel_name="account.move",
        readonly=True)

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Salary Journal',
        domain=[('type', '=', 'general')],
        states={'draft': [('readonly', False)]},
        readonly=True)

    partner_payroll = fields.Many2one(
        string="Partenaire de la paie",
        comodel_name="res.partner")

    @api.onchange('date_start')
    def onchange_date_start(self):
        jour_paye = self.env['ir.config_parameter'].get_param(
            "jour_paiement", 1)
        maintenant = datetime.now()
        date = "%s-%.2d-%.2d" % (
            maintenant.year, maintenant.month, int(jour_paye))
        if self.date_start:
            date = self.date_start[:8] + "%.2d" % int(jour_paye)
        self.date_paiement = date

    @api.multi
    def compute_all_payslip(self):
        for record in self:
            record.slip_ids.filtered(
                lambda x: x.state == "draft").compute_sheet()

    @api.multi
    def set_to_draft(self):
        for record in self:
            for slip in record.slip_ids:
                slip.signal_workflow('cancel_sheet')
                slip.signal_workflow('draft')

    @api.multi
    def validate_payslip(self):
        for record in self:
            for slip in record.slip_ids:
                slip.signal_workflow('hr_verify_sheet')

    @api.multi
    def generate_move(self):
        for record in self.sudo():

            journal = record.journal_id
            period = record.env['account.period'].search([
                ('date_start', '<=', record.date_end),
                ('date_stop', '>=', record.date_end)], limit=1)

            if not journal:
                raise Warning(_("Veuillez renseigner un journal dans le lot"))

            move = {
                'narration': record.name,
                'date': record.date_end,
                'ref': record.name,
                'journal_id': journal.id,
                'period_id': period.id}

            elements = record.get_move_lines()[0]
            move_id = self.env['account.move'].create(move)
            for elt in reversed(elements):
                elt['move_id'] = move_id.id
                self.env['account.move.line'].create(elt)
            record.move = move_id

    @api.model
    def get_move_lines(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')
        slips = self.slip_ids
        rules = slips.mapped('details_by_salary_rule_category.salary_rule_id')
        lines = slips.mapped('details_by_salary_rule_category')

        total_debit = 0
        total_credit = 0

        line_ids = []
        line_ids_report = []
        debit_sum = 0.0
        credit_sum = 0.0

        journal = self.journal_id
        period = self.env['account.period'].search([
            ('date_start', '<=', self.date_end),
            ('date_stop', '>=', self.date_end)], limit=1)

        partner_id = self.partner_payroll.id if self.partner_payroll else None
        if self.move:
            self.move.unlink()

        for rule in rules.filtered(
                lambda x: x.a_comptabiliser).sorted(key=lambda r: r.sequence):
            lines_rule = lines.filtered(
                lambda x: x.salary_rule_id.id == rule.id)
            total = sum(lines_rule.mapped('total'))
            amt = self.credit_note and -total or total
            partner_rule = rule.partner_rule.id if rule.partner_rule else partner_id

            if float_is_zero(amt, precision_digits=precision):
                continue

            if rule.use_personal_account == "no":
                if not rule.account_debit and not rule.account_credit:
                    raise Warning(_(
                        "La regle salariale %s n'a pas de compte debit/credit" % rule.name))

            ana_accounts = lines_rule.mapped(
                'contract_id.analytic_account_id')
            ana_accounts |= lines_rule.mapped(
                'employee_id.department_id.analytic_account_id')
            line_rule_report = {}
            line_rule_report['analytic'] = {}
            line_rule_report['analytic']['lines'] = []

            if rule.is_analytic_account:
                for an_acc in ana_accounts:

                    ana_lines_rule = lines_rule.filtered(
                        lambda x: x.contract_id.analytic_account_id.id == an_acc.id)
                    ana_lines_rule |= lines_rule.filtered(
                        lambda x: not x.contract_id.analytic_account_id and
                        x.employee_id.department_id.analytic_account_id.id == an_acc.id)
                    lines_rule -= ana_lines_rule
                    analytic_account = rule.analytic_account_id or an_acc

                    if rule.use_personal_account != "no":
                        for elt_line in ana_lines_rule:
                            result = self.generate_move_partner(
                                rule, journal, period,
                                analytic_account, elt_line)
                            line_ids.append(result[0])
                            debit_sum += result[1]
                            credit_sum += result[2]
                            line_rule_report['analytic']['lines'].append(result[3])
                    else:
                        result = self.generate_move_rule(
                            ana_lines_rule, rule, journal, period,
                            analytic_account, partner_rule)
                        if result:
                            line_ids.append(result[0])
                            debit_sum += result[1]
                            credit_sum += result[2]
                            line_rule_report['analytic']['lines'].append(result[3])
            if lines_rule:

                if rule.use_personal_account != "no":
                    for elt_line in lines_rule:

                        result = self.generate_move_partner(
                            rule, journal, period, None, elt_line)
                        line_ids.append(result[0])
                        debit_sum += result[1]
                        credit_sum += result[2]
                        line_rule_report['analytic']['lines'].append(result[3])
                else:
                    result = self.generate_move_rule(
                        lines_rule, rule, journal, period,
                        None, partner_rule)
                    if result:
                        line_ids.append(result[0])
                        debit_sum += result[1]
                        credit_sum += result[2]
                        line_rule_report['analytic']['lines'].append(result[3])

            # lignes pour le rapport
            line_rule_report['rule_name'] = rule.name

            # calcul du total analytique
            total_deb_ana = sum([x['debit'] for x in line_rule_report['analytic']['lines']])
            total_crd_ana = sum([x['credit'] for x in line_rule_report['analytic']['lines']])
            line_rule_report['analytic']['total_db'] = total_deb_ana
            line_rule_report['analytic']['total_cd'] = total_crd_ana
            if rule.account_debit:
                line_rule_report['account_code'] = rule.account_debit.code
                line_rule_report['account_name'] = rule.account_debit.name
                line_rule_report['debit'] = self.credit_note and -total or total
                line_rule_report['credit'] = 0
            elif rule.account_credit:
                line_rule_report['account_code'] = rule.account_credit.code
                line_rule_report['account_name'] = rule.account_credit.name
                line_rule_report['debit'] = 0
                line_rule_report['credit'] = self.credit_note and -total or total
            else:
                line_rule_report['account_code'] = ""
                line_rule_report['account_name'] = "Compte personnel"
                if rule.use_personal_account == "debit":
                    line_rule_report['debit'] = self.credit_note and -total or total
                    line_rule_report['credit'] = 0
                elif rule.use_personal_account == "credit":
                    line_rule_report['debit'] = 0
                    line_rule_report['credit'] = self.credit_note and -total or total
                else:
                    line_rule_report['debit'] = ""
                    line_rule_report['credit'] = ""
            line_rule_report['total'] = amt
            line_ids_report.append(line_rule_report)

        # get the total debit and credit
        total_debit = debit_sum
        total_credit = credit_sum

        if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
            acc_id = journal.default_credit_account_id.id
            if not acc_id:
                raise Warning(_('The Expense Journal "%s" has not properly configured the Credit Account!')%(journal.name))
            adjust_sum = debit_sum - credit_sum
            total_credit += adjust_sum
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'date': self.date_end,
                'partner_id': partner_id,
                'account_id': acc_id,
                'journal_id': journal.id,
                'period_id': period.id,
                'debit': 0.0,
                'credit': adjust_sum,
            }
            line_ids.append(adjust_credit)

            line_rule_report = {}
            line_rule_report['analytic'] = {}
            line_rule_report['analytic']['lines'] = []
            line_rule_report['rule_name'] = _('Adjustment Entry')
            line_rule_report['account_code'] = journal.default_credit_account_id.code
            line_rule_report['account_name'] = journal.default_credit_account_id.name
            line_rule_report['debit'] = 0
            line_rule_report['credit'] = debit_sum - credit_sum
            line_ids_report.append(line_rule_report)

        elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
            acc_id = journal.default_debit_account_id.id
            if not acc_id:
                raise Warning(_('The Expense Journal "%s" has not properly configured the Debit Account!')%(journal.name))
            adjust_sum = credit_sum - debit_sum
            total_debit += adjust_sum
            adjust_debit = {
                'name': _('Adjustment Entry'),
                'date': self.date_end,
                'partner_id': partner_id,
                'account_id': acc_id,
                'journal_id': journal.id,
                'period_id': period.id,
                'debit': credit_sum - debit_sum,
                'credit': 0.0,
            }
            line_ids.append(adjust_debit)

            line_rule_report = {}
            line_rule_report['analytic'] = {}
            line_rule_report['analytic']['lines'] = []
            line_rule_report['analytic']['total_db'] = 0
            line_rule_report['analytic']['total_cd'] = 0
            line_rule_report['rule_name'] = _('Adjustment Entry')
            line_rule_report['account_code'] = journal.default_debit_account_id.code
            line_rule_report['account_name'] = journal.default_debit_account_id.name
            line_rule_report['debit'] = credit_sum - debit_sum
            line_rule_report['credit'] = 0
            line_ids_report.append(line_rule_report)

        line_rule_report = {}
        line_rule_report['analytic'] = {}
        line_rule_report['analytic']['lines'] = []
        line_rule_report['analytic']['total_db'] = 0
        line_rule_report['analytic']['total_cd'] = 0
        line_rule_report['rule_name'] = _('Adjustment Entry')
        line_rule_report['account_code'] = ""
        line_rule_report['account_name'] = ""
        line_rule_report['debit'] = total_debit
        line_rule_report['credit'] = total_credit
        line_ids_report.append(line_rule_report)

        return (line_ids, line_ids_report)

    @api.model
    def generate_move_partner(self, rule, journal, period,
                              analytic_account, elt_line):
        employee = elt_line.employee_id
        partner = elt_line.mapped("employee_id.address_home_id")
        contrat = elt_line.contract_id
        part_acc = elt_line.contract_id.personal_account_id

        if not partner:
            raise Warning(_(
                "L'employe %s n'a pas de partenaire rattache" % employee.name))

        if not part_acc:
            raise Warning(_(
                "Renseignez le compte personnel du contrat %s" % contrat.name))

        name_line = rule.name
        name_line += " %s " % employee.name
        if analytic_account:
            name_line += "(%s)" % analytic_account.name

        account_id = part_acc if part_acc else partner.property_account_payable
        total = elt_line.total
        amt = self.credit_note and -total or total
        dbt_sum = 0
        cdt_sum = 0
        analytic_account_id = analytic_account.id if analytic_account else None

        if rule.use_personal_account == "debit":
            amount_debit = amt > 0.0 and amt or 0.0
            amount_credit = amt < 0.0 and -amt or 0.0
            dbt_sum = amount_debit - amount_credit
        else:
            amount_debit = amt < 0.0 and -amt or 0.0
            amount_credit = amt > 0.0 and amt or 0.0
            cdt_sum += amount_credit - amount_debit

        mv_line = {
            'name': name_line,
            'date': self.date_end,
            'partner_id': partner.id,
            'account_id': account_id.id,
            'journal_id': journal.id,
            'period_id': period.id,
            'debit': amount_debit,
            'credit': amount_credit,
            'analytic_account_id': analytic_account_id}

        s_compte = analytic_account.name if analytic_account else ""
        s_nom_compte = account_id.code if account_id else ""

        line_analytic = {
            'compte': s_compte,
            'nom_cpt': "%s - %s" % (s_nom_compte, partner.name),
            'debit': amount_debit,
            'credit': amount_credit
        }

        return (mv_line, dbt_sum, cdt_sum, line_analytic)

    @api.model
    def generate_move_rule(self, lines_rule, rule, journal, period,
                           analytic_account, partner_id):
        total = sum(lines_rule.mapped('total'))
        amt = self.credit_note and -total or total
        dbt_sum = 0
        cdt_sum = 0

        name_line = rule.name
        if analytic_account:
            name_line += "(%s)" % analytic_account.name

        analytic_account_id = analytic_account.id if analytic_account else None

        if rule.account_debit:

            debit_line = {
                'name': name_line,
                'date': self.date_end,
                'partner_id': partner_id,
                'account_id': rule.account_debit.id,
                'journal_id': journal.id,
                'period_id': period.id,
                'debit': amt > 0.0 and amt or 0.0,
                'credit': amt < 0.0 and -amt or 0.0,
                'analytic_account_id': analytic_account_id
            }

            line_analytic = {
                'compte': analytic_account.code if analytic_account else "PAS DE COMPTABILISATION",
                'nom_cpt': analytic_account.name if analytic_account else "",
                'debit': amt > 0.0 and amt or 0.0,
                'credit': amt < 0.0 and -amt or 0.0
            }
            dbt_sum = debit_line['debit'] - debit_line['credit']
            return (debit_line, dbt_sum, 0, line_analytic)

        if rule.account_credit:

            credit_line = {
                'name': name_line,
                'date': self.date_end,
                'partner_id': partner_id,
                'account_id': rule.account_credit.id,
                'journal_id': journal.id,
                'period_id': period.id,
                'debit': amt < 0.0 and -amt or 0.0,
                'credit': amt > 0.0 and amt or 0.0,
                'analytic_account_id': analytic_account_id
            }

            line_analytic = {
                'compte': analytic_account.code if analytic_account else "PAS DE COMPTABILISATION",
                'nom_cpt': analytic_account.name if analytic_account else "",
                'debit': amt < 0.0 and -amt or 0.0,
                'credit': amt > 0.0 and amt or 0.0
            }
            cdt_sum += credit_line['credit'] - credit_line['debit']
            return (credit_line, 0, cdt_sum, line_analytic)

    @api.constrains('date_paiement')
    def check_date_paiement(self):
        for record in self:
            if not record.date_paiement:
                jour_paye = record.env['ir.config_parameter'].get_param(
                    "jour_paiement", 1)
                maintenant = datetime.now()
                date = "%s-%.2d-%.2d" % (
                    maintenant.year, maintenant.month, int(jour_paye))
                if record.date_start:
                    date = record.date_start[:8] + "%.2d" % int(jour_paye)
                record.date_paiement = date
