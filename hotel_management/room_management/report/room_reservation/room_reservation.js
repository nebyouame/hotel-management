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
        // {
        //     "fieldname": "menu_type",
        //     "label": __("Menu Type"),
        //     "fieldtype": "Link",
        //     "options": "Menu Type"
        // }
	]
};
