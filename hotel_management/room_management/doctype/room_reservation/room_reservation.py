# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document

def changeRoomStatus(roomId,status):
	doc = frappe.get_doc('Room', roomId)
	if(status != doc.status):
		doc.status = status
		doc.save()
class RoomReservation(Document):
	def validate(self):
		for each_child_doc in self.rooms_for_reservation:
			each_child_doc.before_save()

	def before_save(self):
		print("before_save")
		for reservation in self.rooms_for_reservation:
			sReservation = frappe.get_all('Single Reservations', filters={'room': reservation.room ,"reservation_date": ["between",  (reservation.starts_on, reservation.ends_on)]}, fields=['name','reservation_date'])
			if(len(sReservation)):
				# frappe.msgprint(f"Room {reservation.room} alradiy reserved on {sReservation[0].reservation_date}.","Error")
				frappe.throw(
					title='Error',
					msg=f"Room {reservation.room} already reserved on {sReservation[0].reservation_date}.",
				)
		# for reservation in self.rooms_for_reservation:
		# 	print("ends_on: ",reservation.ends_on)
		# 	value =frappe.db.sql_list(f"select name,starts_on,ends_on FROM `tabReserved Room` WHERE room = {reservation.room} and ((starts_on >= '{reservation.starts_on}' and starts_on <= '{reservation.ends_on}') or (starts_on <= '{reservation.starts_on}' and ends_on >= '{reservation.ends_on}') or (ends_on >= '{reservation.starts_on}' and ends_on <= '{reservation.ends_on}'))")
		# 	# value =frappe.db.sql_list(f"select name,starts_on,ends_on FROM `tabReserved Room` WHERE starts_on < '{reservation.starts_on}'")
		# 	# value = frappe.db.get_list('Reserved Room', filters=[
		# 	# 	['ends_on', '<=', reservation.ends_on],
		# 	# 	['starts_on', '>=', reservation.starts_on]
		# 	# ], fields=["ends_on"])
		# 	# print("value: ",value)
		# 	# print("my value: ",reservation.name)
		# 	# print("save: ",reservation.get('__unsaved'))
		# 	changeRoomStatus(reservation.room,"Reserved")
		# 	# print(reservation.type)

		# 	start = datetime.strptime(reservation.starts_on, '%Y-%m-%d')
		# 	ends_on = datetime.strptime(reservation.ends_on, '%Y-%m-%d')
		# 	delta = timedelta(days=1)
		# 	print(reservation.type)
		# 	print(reservation.room)
		# 	print(reservation.price)
		# 	print(start)
		# 	print(reservation._parent_doc)
		# 	print(reservation.name)
		# 	while start <= ends_on:
		# 		try:
		# 			single_r = frappe.get_doc(
		# 				{
		# 					"doctype": "Single Reservations",
		# 					"type": reservation.type,
		# 					"room": reservation.room,
		# 					"price": reservation.price,
		# 					"reservation_date": start,
		# 					# "room_reservation_id": reservation._parent_doc,
		# 					# "child_table_id": reservation.name,
		# 				}
		# 			)
		# 			data = single_r.insert()
		# 			frappe.db.commit()
		# 			start += delta
		# 		except:
		# 			start += delta
		# 			pass
	def after_save(self):
		print("after")
	def on_update(self):
		print("on_update")
	def after_insert(self):
		print("after_insert")
		for reservation in self.rooms_for_reservation:
			changeRoomStatus(reservation.room,"Reserved")
			start = datetime.strptime(reservation.starts_on, '%Y-%m-%d')
			ends_on = datetime.strptime(reservation.ends_on, '%Y-%m-%d')
			delta = timedelta(days=1)
			while start <= ends_on:
				try:
					single_r = frappe.get_doc(
						{
							"doctype": "Single Reservations",
							"type": reservation.type,
							"room": reservation.room,
							"price": reservation.price,
							"reservation_date": start,
							"room_reservation_id": reservation._parent_doc,
							"child_table_id": reservation.name,
						}
					)
					data = single_r.insert()
					frappe.db.commit()
					start += delta
				except:
					start += delta
					pass
