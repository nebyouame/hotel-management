# Copyright (c) 2024, Powerware Technologies and contributors 
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    # Define columns
    columns = [
        {"label": _("Hotel Order"), "fieldname": "hotel_order", "fieldtype": "Link", "options": "Hotel Order"},
        {"label": _("Menu"), "fieldname": "menu", "fieldtype": "Link", "options": "Menu"},
        {"label": _("Total Amount(VAT)"), "fieldname": "amount", "fieldtype": "Currency"}
    ]
    
    # Initialize conditions
    conditions = ""
    
    # Apply filters
    if filters.get("from_date"):
        conditions += " AND h.creation >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND h.creation <= %(to_date)s"
    if filters.get("ord_status"):
        conditions += " AND h.status = %(ord_status)s"
    
    
    if filters.get("menu_type"):
        conditions += """ 
        AND i.item_code IN (
            SELECT name FROM `tabMenu`
            WHERE menu_type = %(menu_type)s
        )
        """
    

    if filters.get("menu"):
        conditions += """
        AND i.item_code = %(menu)s
        """
    
  
    if filters.get("paid_by"):
        conditions += """
        AND h.modified_by = %(paid_by)s
        AND h.status = 'Paid'
        """
    
   
    data = frappe.db.sql(f"""
        SELECT
            h.name as hotel_order,
            i.item_code as menu,
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
    
    # Calculate the total VAT
    total_amount = sum(row['amount'] for row in data if row['amount'])  # Ensure to handle None values
    
    # Add total VAT to the data if data exists
    if data:
        data.append({
            "hotel_order": _("Total Amount"),
            "amount": total_amount
        })
    
    return columns, data
