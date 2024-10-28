from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def create_delivery_note_for_menu(menu_name, qty):
    qty_to_deliver = float(qty)

    # Get items linked to the menu name
    items_linked_to_menu = frappe.get_list('Item', 
                                           filters={'menuu': menu_name},
                                           fields=['name', 'item_code'])

    # If no items are linked to the menu, simply pass
    if not items_linked_to_menu:
        return  # Just return without any action if no items are found

    # Fetch one customer from the Customer list
    customer = frappe.get_list('Customer', fields=['name'], limit=1)
    if not customer:
        frappe.throw("No customers available in the system.")

    # Create a new Delivery Note document
    delivery_note = frappe.new_doc('Delivery Note')
    delivery_note.customer = customer[0].name  # Set the customer to the first in the list
    delivery_note.company = frappe.defaults.get_user_default("company")
    delivery_note.posting_date = frappe.utils.nowdate()
    delivery_note.posting_time = frappe.utils.nowtime()

    for linked_item in items_linked_to_menu:
        # Check if the item exists in the Item doctype
        if not frappe.db.exists('Item', linked_item['item_code']):
            # If the item does not exist, skip to the next item
            frappe.msgprint(f"Item code {linked_item['item_code']} does not exist. Skipping.")
            continue  # Skip this iteration

        # Get the item document to retrieve its default warehouse from item_defaults table
        item_doc = frappe.get_doc('Item', linked_item['item_code'])
        
        # Check if item_defaults table has any entries
        if not item_doc.item_defaults:
            frappe.msgprint(f"No default warehouse set for item {linked_item['item_code']}. Skipping.")
            continue  # Skip this item if no default warehouse is found

        # Get the default warehouse from the item_defaults table
        default_warehouse = None
        for item_default in item_doc.item_defaults:
            default_warehouse = item_default.default_warehouse
            if default_warehouse:
                break  # Get the first available default warehouse

        if not default_warehouse:
            frappe.msgprint(f"No default warehouse found for item {linked_item['item_code']}. Skipping.")
            continue  # Skip this item if no default warehouse is found

        # Add items to the Delivery Note
        delivery_note.append("items", {
            "item_code": linked_item['item_code'],
            "qty": qty_to_deliver,
            "warehouse": default_warehouse,  # Use the retrieved default warehouse
        })

    # Save and submit the Delivery Note if there are items to deliver
    if delivery_note.items:
        try:
            delivery_note.save(ignore_permissions=True)
            delivery_note.submit()
            frappe.db.commit()  # Commit changes to database
            frappe.msgprint(f"Delivery Note {delivery_note.name} created successfully.")
            return delivery_note.name
        except frappe.exceptions.ValidationError as e:
            frappe.throw(f"Failed to create Delivery Note: {str(e)}")
