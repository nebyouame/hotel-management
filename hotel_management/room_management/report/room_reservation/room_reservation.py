# Copyright (c) 2024, Powerware Tecnologies  and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
    
	columns = [
        {"label": _("room_reservation_id"), "fieldname": "room_reservation_id", "fieldtype": "Link", "options": "Room Reservation"},
        {"label": _("room_type"), "fieldname": "room_type", "fieldtype": "Link", "options": "Room Type"},
        {"label": _("room"), "fieldname": "room", "fieldtype": "Link", "options": "Room"},
        {"label": _("number_of_day"), "fieldname": "number_of_day", "fieldtype": "Int"},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency"},
        {"label": _("payment_date"), "fieldname": "payment_date", "fieldtype": "Date"}
    ]
	conditions = ""
	if filters.get("from_date"):
		conditions += " AND rp.payment_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " AND rp.payment_date <= %(to_date)s"
	if filters.get("room_type"):
		conditions += "AND rr.type = %(room_type)s"
	if filters.get("room"):
		conditions += "AND rr.room = %(room)s"

	data = frappe.db.sql(f"""
		SELECT
			sr.room_reservation_id as room_reservation_id,
			sr.name,
			sr.child_table_id as reserved_room_id,
			rr.type as room_type,
			rr.room as room,
			rp.days as number_of_day,
			rp.amount as amount,
			rp.payment_date as payment_date,	
			rp.owner as owner			
		FROM
			`tabSingle Reservations` sr
		JOIN
			`tabRoom Reservation` rre ON rre.name = sr.room_reservation_id
		JOIN
			`tabReserved Room` rr ON rr.parent = sr.room_reservation_id
		JOIN
			`tabRoom Payment` rp ON rp.room = sr.name
		WHERE
			1=1 {conditions}
	""", filters, as_dict=1)

	# print("report data: ", data)

	# total_quantity = sum(row['quantity'] for row in data)
	total_amount = sum(row['amount'] for row in data)

	if data:
		data.append({
			"room_reservation_id": _("Total Amount"),
			# "quantity": total_quantity,
			"amount": total_amount
		})

	return columns, data
