# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xlwt
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
from openerp.exceptions import Warning
_logger = logging.getLogger(__name__)


class dipes_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(dipes_xls_parser, self).__init__(
            cr,
            uid,
            name,
            context=context)
        self.context = context
        wanted_list = None
        template_changes = None
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes})


class dipes_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(dipes_xls, self).__init__(
            name, table, rml, parser, header, store)

        # XLS Template Journal Items
        self.col_specs_lines_template = {
            'move_name': {
                'header': [1, 20, 'text', _render("_('Entry')")],
                'lines': [1, 0, 'text', _render("GOGO")]}
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        report_name = _("DIPES")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        for dipe in _p['dipes']:
            # Title
            c_specs = [('ligne', 1, 0, 'text', dipe)]
            row_data = self.xls_row_template(c_specs, ['ligne'])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

dipes_xls('report.corpe_paie.dipes_mensuel.xls', 'hr.employee', parser=dipes_xls_parser)
