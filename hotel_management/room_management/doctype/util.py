from datetime import date
import frappe

@frappe.whitelist()
def get_Reservation():
	"""Returns events for Gantt / Calendar view rendering.
	"""
	
	data = frappe.db.sql("""
		SELECT CONCAT('Room: ', room) as title, room,'#FF5733' as color, starts_on, ends_on FROM `tabReserved Room`;
		""", as_dict=True)
	return data

@frappe.whitelist()
def get_Reservation_between_date(ends_on,starts_on ):
	sReservation = frappe.get_all('Single Reservations', filters={"reservation_date": ["between",  (starts_on, ends_on)], "status": "Check-in"}, fields=['room'])
	arrayOfSreservation = []
	for s in sReservation:
		arrayOfSreservation.append(s.room)
	sReservation = frappe.get_all('Room', filters={"room_number": ["in",  arrayOfSreservation]}, fields=['room_number'])
	print("sReservation :", sReservation)
	arrayOfSreservation = []
	for s in sReservation:
		arrayOfSreservation.append(s.room_number)
	print("arrayOfSreservation :", arrayOfSreservation)

	return arrayOfSreservation