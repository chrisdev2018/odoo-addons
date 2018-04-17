# -*-coding: utf-8 -*-
from openerp import models, fields, api

class Wizard(models.TransientModel):

    _name = "openacademy.wizard"

    def _default_session(self):
        self.env['openacademy.session'].browse(self._context.get('active_id'))

    session_id = fields.Many2one('openacademy.session',
                                 string="session", required=True)

    attendee_ids = fields.Many2many('res.partner', string="Participants")

