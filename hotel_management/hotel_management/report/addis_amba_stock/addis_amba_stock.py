import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    # Define the columns for the report
    columns = [
        {"label": _("Hotel Order"), "fieldname": "hotel_order", "fieldtype": "Link", "options": "Hotel Order"},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item"},
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Data"},
        {"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float"},
        {"label": _("Incoming Rate"), "fieldname": "incoming_rate", "fieldtype": "Currency"},
        {"label": _("Selling Price"), "fieldname": "selling_price", "fieldtype": "Currency"},
        {"label": _("Total Incoming Rate"), "fieldname": "total_incoming_rate", "fieldtype": "Currency"},
        {"label": _("Total Selling Price"), "fieldname": "total_selling_price", "fieldtype": "Currency"},
        {"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency"},
        # {"label": _("Voucher No"), "fieldname": "voucher_no", "fieldtype": "Link", "options": "Delivery Note"},
    ]
    
    # Initialize conditions
    conditions = []

    # Apply filters
    if filters.get("company"):
        conditions.append("sle.company = %(company)s")
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("DATE(sle.posting_date) BETWEEN %(from_date)s AND %(to_date)s")
    elif filters.get("from_date"):
        conditions.append("DATE(sle.posting_date) >= %(from_date)s")
    elif filters.get("to_date"):
        conditions.append("DATE(sle.posting_date) <= %(to_date)s")
    
    if filters.get("item_code"):
        conditions.append("sle.item_code = %(item_code)s")

    # Only fetch entries related to Delivery Note voucher types
    conditions.append("sle.voucher_type = 'Delivery Note'")
    
    condition_str = " AND ".join(conditions) if conditions else "1=1"
    
    # Execute the query to get stock ledger entries
    data = frappe.db.sql(f"""
        SELECT
            sle.item_code,
            sle.stock_uom,
            sle.actual_qty AS out_qty,
            sle.incoming_rate,
            ABS(sle.incoming_rate * sle.actual_qty) AS total_incoming_rate,  -- Calculate Total Incoming Rate (absolute value)
            ip.price_list_rate AS selling_price,
            ABS(ip.price_list_rate * sle.actual_qty) AS total_selling_price,  -- Calculate Total Selling Price (absolute value)
            sle.voucher_no,
            ho.name AS hotel_order
        FROM
            `tabStock Ledger Entry` sle
        LEFT JOIN
            `tabDelivery Note` dn ON dn.name = sle.voucher_no
        LEFT JOIN
            `tabHotel Order` ho ON ho.name = dn.hotel_order
        LEFT JOIN
            `tabItem Price` ip ON ip.item_code = sle.item_code
        WHERE
            {condition_str}
        ORDER BY
            sle.posting_date DESC
    """, filters, as_dict=1)

    # Calculate the total outgoing quantity (sum of actual_qty)
    total_out_qty = sum(row['out_qty'] for row in data if row['out_qty'])
    
    # Calculate the total incoming rate (sum of incoming_rate * actual_qty)
    # total_incoming_rate = sum(row['incoming_rate'] * row.get('out_qty', 0) for row in data if row['incoming_rate'])
    
    # Calculate the total selling price (sum of selling_price * actual_qty)
    # total_selling_price = sum(row['selling_price'] * row.get('out_qty', 0) for row in data if row['selling_price'])
    
    # Calculate the total total selling price (sum of ABS(total_selling_price))
    total_absolute_selling_price = sum(row['total_selling_price'] for row in data)

    # Calculate the total total incoming rate (sum of ABS(total_incoming_rate))
    total_absolute_incoming_rate = sum(row['total_incoming_rate'] for row in data)
    
    # Calculate the total profit (Total Selling Price - Total Incoming Rate)
    total_profit = total_absolute_selling_price - total_absolute_incoming_rate

    # Add profit for each row (Total Selling Price - Total Incoming Rate)
    for row in data:
        row['profit'] = row.get('total_selling_price', 0) - row.get('total_incoming_rate', 0)

    if data:
        # Add the total row to the report
        data.append({
            "hotel_order": _("Total"),
            "out_qty": total_out_qty,
            # "incoming_rate": total_incoming_rate,
            "total_incoming_rate": total_absolute_incoming_rate,
            # "selling_price": total_selling_price,
            "total_selling_price": total_absolute_selling_price,
            "profit": total_profit  # Add total profit to the total row
        })
    
    return columns, data
