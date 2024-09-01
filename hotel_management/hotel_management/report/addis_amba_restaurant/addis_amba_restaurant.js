// Copyright (c) 2024, Powerware Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Restaurant Order"] = {
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
            "fieldname": "ord_status",
            "label": __("Order Status"),
            "fieldtype": "Select",
            "options": "\nUnpaid\nPaid"
        }
    ]
};
