from openerp.osv import osv
from openerp.osv import fields


class personne(osv.osv):
	_name="personne"
	_descrption="Personnes"
	_columns = {
			'name' : fields.char('Name', size=64, required=True, select=True),
			#'description' : fields.text('Description'),
			'age' : fields.text('Age')

	}

	
		