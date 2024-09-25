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
    conditions = []
    
    # Apply filters
    if filters.get("ord_status"):
        conditions.append("h.status = %(ord_status)s")
    
    if filters.get("menu_type"):
        conditions.append(""" 
        i.item_code IN (
            SELECT name FROM `tabMenu`
            WHERE menu_type = %(menu_type)s
        )
        """)
    
    if filters.get("menu"):
        conditions.append("i.item_code = %(menu)s")
    
    if filters.get("paid_by"):
        conditions.append("h.owner = %(paid_by)s")

    # Date filtering directly in the SQL statement
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("DATE(h.creation) BETWEEN %(from_date)s AND %(to_date)s")
    elif filters.get("from_date"):
        conditions.append("DATE(h.creation) >= %(from_date)s")
    elif filters.get("to_date"):
        conditions.append("DATE(h.creation) <= %(to_date)s")

    # Combine conditions
    condition_str = " AND ".join(conditions) if conditions else "1=1"
    
    data = frappe.db.sql(f"""
        SELECT
            h.name AS hotel_order,
            i.item_code AS menu,
            i.amount AS amount
        FROM
            `tabHotel Order` h
        JOIN
            `tabHotel Order Item` i ON i.parent = h.name
        WHERE
            {condition_str}
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
