# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

# import frappe
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ReservedRoom(Document):
	def before_save(self):
		print("check_out_time ",self.check_out_time == None)
		if self.status == "Check-in" and self.check_in_time == None:
			self.check_in_time = now_datetime()
		if self.status == "Check-out" and self.check_out_time == None:
			self.check_out_time = now_datetime()
			frappe.db.set_value("Room",self.room,"status","Unreserved")

		
