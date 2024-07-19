# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

# import frappe
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document


class ReservedRoom(Document):
	def before_save(self):
		print("parnet doc ",self._parent_doc)
		print("child save: ",self.get('__unsaved'))
		
