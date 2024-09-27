// Copyright (c) 2024, Powerware Tecnologies  and contributors
// For license information, please see license.txt

frappe.query_reports["Room Reservation"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.nowdate()
        },
        {
            "fieldname": "room_type",
            "label": __("Room Type"),
            "fieldtype": "Link",
            "options": "Room Type"
        },
        {
            "fieldname": "room",
            "label": __("Room"),
            "fieldtype": "Link",
            "options": "Room"
        }
	]
};
