from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def create_delivery_note(menu_name, qty, hotel_order_name=None):
    qty_to_deliver = float(qty)

    items_linked_to_menu = frappe.get_list('Item', 
                                           filters={'menuu': menu_name},
                                           fields=['name', 'item_code'])

    if not items_linked_to_menu:
        return  

    customer = frappe.get_list('Customer', fields=['name'], limit=1)
    if not customer:
        frappe.throw("No customers available in the system.")

    delivery_note = frappe.new_doc('Delivery Note')
    delivery_note.customer = customer[0].name
    delivery_note.company = frappe.defaults.get_user_default("company")
    delivery_note.posting_date = frappe.utils.nowdate()
    delivery_note.posting_time = frappe.utils.nowtime()

    if hotel_order_name:
        delivery_note.hotel_order = hotel_order_name

    for linked_item in items_linked_to_menu:
        if not frappe.db.exists('Item', linked_item['item_code']):
            frappe.msgprint(f"Item code {linked_item['item_code']} does not exist. Skipping.")
            continue

        item_doc = frappe.get_doc('Item', linked_item['item_code'])
        
        if not item_doc.item_defaults:
            frappe.msgprint(f"No default warehouse set for item {linked_item['item_code']}. Skipping.")
            continue

        default_warehouse = None
        for item_default in item_doc.item_defaults:
            default_warehouse = item_default.default_warehouse
            if default_warehouse:
                break

        if not default_warehouse:
            frappe.msgprint(f"No default warehouse found for item {linked_item['item_code']}. Skipping.")
            continue

        delivery_note.append("items", {
            "item_code": linked_item['item_code'],
            "qty": qty_to_deliver,
            "warehouse": default_warehouse, 
        })

    if delivery_note.items:
        try:
            delivery_note.save(ignore_permissions=True)
            delivery_note.submit()
            frappe.db.commit()
            frappe.msgprint(f"Delivery Note {delivery_note.name} created successfully.")
            return delivery_note.name
        except frappe.exceptions.ValidationError as e:
            frappe.throw(f"Failed to create Delivery Note: {str(e)}")
    
