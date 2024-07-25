# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class SingleReservations(Document):
	def validate(self):
		Reserved_Room = frappe.get_all('Reserved Room', filters={'name': self.child_table_id},fields=['parent'])
		print("Reserved_Room: ",Reserved_Room[0])
		self.room_reservation_id = Reserved_Room[0].parent

