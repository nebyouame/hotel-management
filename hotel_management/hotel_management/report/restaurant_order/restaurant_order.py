# Copyright (c) 2024, Powerware Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    columns = [
        {"label": _("Hotel Order"), "fieldname": "hotel_order", "fieldtype": "Link", "options": "Hotel Order"},
        {"label": _("Quantity"), "fieldname": "quantity", "fieldtype": "Int"},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency"},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency"}
    ]
    
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND h.order_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND h.order_date <= %(to_date)s"
    if filters.get("menu_type"):
        conditions += " AND i.item_code IN (SELECT name FROM `tabMenu` WHERE menu_type = %(menu_type)s)"
    
    data = frappe.db.sql(f"""
        SELECT
            h.name as hotel_order,
            h.table_order_no as table_no,
            h.waiter as waiter,
            i.item_code as menu,
            i.qty as quantity,
            i.chief as assigned_employee,
            i.rate as rate,
            i.amount as amount
        FROM
            `tabHotel Order` h
        JOIN
            `tabHotel Order Item` i ON i.parent = h.name
        WHERE
            1=1 {conditions}
        ORDER BY
            h.order_date DESC
    """, filters, as_dict=1)
    
    total_quantity = sum(row['quantity'] for row in data)
    total_amount = sum(row['amount'] for row in data)
    
    if data:
        data.append({
            "hotel_order": _("Total Amount"),
            "quantity": total_quantity,
            "amount": total_amount
        })
    
    return columns, data
