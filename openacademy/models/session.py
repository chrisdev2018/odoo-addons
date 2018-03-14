# -*-coding: utf-8 -*-
from openerp import models, fields, api


class Session(models.Model):
	_name='openacademy.session'

	name = fields.Char(striing="Nom", required=True)

	start_date = fields.Date(string="Date de debut")

	duration = fields.Float(digit=(6,2), string="Duree", help="Duration in days")

	seats = fields.Float(string="Nombre de places")

	instructor_id = fields.Many2one('res.partner', string="Instructeur")

	course_id = fields.Many2one('openacademy.course', ondelete='cascade',
								string="Cours", required=True)



	attendee_ids = fields.Many2many('openacademy.attendee',
									string='Liste des participants ')
	taken_seats = fields.Float(string="Pourcentage de places prises",
							   compute='_taken_seats')

	state = fields.Selection([
			('draft','Draft'),
			('confirmed','Confirmed'),
			('done','Done'),
		], default='draft')


	@api.multi
	def action_draft(self):
		self.state='draft'

	@api.multi
	def action_confirm(self):
		self.state='confirmed'
		
	@api.multi
	def action_done(self):
		self.state='done'		

	@api.depends('seats', 'attendee_ids')
	def _taken_seats(self):
		for p in self:
			if not p.seats:
				p.taken_seats=0.0
			else:
				p.taken_seats=100.0*len(p.attendee_ids)/p.seats



	@api.onchange('seats', 'attendee_ids')
	def ver(self):
		if self.seats<0:
			return{
				'warning':{
					'title':"Nombres de places incorrects",
					'message':"Le nombre ne saurai etre negatif",
				},

			}
		if self.seats<len(self.attendee_ids):
			return {
				'warning':{
					'title':"Trop de participants",
					'message':"Ajouter le nombre de places ou reduire le nombre de participants",
				},
			}