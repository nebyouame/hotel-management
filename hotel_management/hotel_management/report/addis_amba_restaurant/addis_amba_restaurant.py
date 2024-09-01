# Copyright (c) 2024, Powerware Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    columns = [
        {"label": _("Hotel Order"), "fieldname": "hotel_order", "fieldtype": "Link", "options": "Hotel Order"},
        {"label": _("Total Amount(VAT)"), "fieldname": "tot_vat", "fieldtype": "Currency"}
    ]
    
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND h.order_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND h.order_date <= %(to_date)s"
    if filters.get("ord_status"):
        conditions += " AND h.status = %(ord_status)s"
    
    data = frappe.db.sql(f"""
        SELECT
            h.name as hotel_order,
            h.tot_vat as tot_vat
        FROM
            `tabHotel Order` h
        WHERE
            1=1 {conditions}
        ORDER BY
            h.order_date DESC
    """, filters, as_dict=1)
    
    total_vat = sum(row['tot_vat'] for row in data if row['tot_vat'])  # Ensure to handle None values
    
    if data:
        data.append({
            "hotel_order": _("Total Amount"),
            "tot_vat": total_vat
        })
    
    return columns, data
