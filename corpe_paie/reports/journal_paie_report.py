# -*-coding: utf-8 -*-
from openerp import api, models
import re


def format_float(value):
    return '{:,.1f}'.format(value).replace(',', ' ')


class BmqMagReport(models.AbstractModel):
    _name = 'report.corpe_paie.journal_paie_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'corpe_paie.journal_paie_template')

        infos = {}
        result = {}

        lots = self.env["hr.payslip.run"].browse(self._ids)
        result = lots.get_move_lines()[1]
        infos['lot'] = ','.join(lots.mapped("name"))

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': result,
            'infos': infos
        }
        return report_obj.render(
            'corpe_paie.journal_paie_template', docargs)
