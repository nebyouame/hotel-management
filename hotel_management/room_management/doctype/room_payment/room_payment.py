# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils.data import now_datetime


class RoomPayment(Document):
	def before_save(self):
		print("payment_date: ",self.payment_date)
		if self.payment_date == None:
			self.payment_date = now_datetime()
