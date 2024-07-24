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
			sReservation = frappe.get_all('Single Reservations', filters={'room': reservation.room ,"reservation_date": ["between",  (reservation.starts_on, reservation.ends_on)]}, fields=['child_table_id','reservation_date'])
			print("len: ",len(sReservation))
			print("sReservation: ", sReservation)
			if(len(sReservation)):
				if(sReservation[0].child_table_id == reservation.name ):
					pass
				else:
					print("error info: ",sReservation, reservation)
					frappe.throw(
						title='Error',
						msg=f"Room {reservation.room} already reserved on {sReservation[0].reservation_date}.",
					)
	def on_update(self):
		print("on_update")
		for reservation in self.rooms_for_reservation:
			sReservation = frappe.get_all('Single Reservations', filters={'room': reservation.room ,"reservation_date": ["between",  (reservation.starts_on, reservation.ends_on)]}, fields=['child_table_id','reservation_date'])
			if(len(sReservation) == 0):
				print("reservation",reservation)
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
	def after_insert(self):
		print("after_insert")
		for reservation in self.rooms_for_reservation:
			print("reservation",reservation)
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
