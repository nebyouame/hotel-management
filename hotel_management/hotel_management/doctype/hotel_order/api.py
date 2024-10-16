
from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def update_stock_entry_qty(menu_name, qty):
        qty_to_deduct = float(qty) 
        # Step 1: Find all items linked to the provided menu_name via the 'menuu' field in the Item doctype
        items_linked_to_menu = frappe.get_list('Item', 
                                               filters={'menuu': menu_name},
                                               fields=['name', 'item_code'])

        if items_linked_to_menu:
            # Step 2: Iterate through each item linked to the menu
            for linked_item in items_linked_to_menu:
                # Step 3: Find all Stock Entry Details with the matching item_code
                stock_entries = frappe.get_list('Stock Entry Detail', 
                                                filters={'item_code': linked_item['item_code']},
                                                fields=['parent', 'name', 'qty'])

                if stock_entries:
                    for entry in stock_entries:
                        # Step 4: Load the Stock Entry document that this detail belongs to
                        stock_entry = frappe.get_doc('Stock Entry', entry['parent'])
                        
                        # Step 5: Get the Stock Entry Detail row for the item_code
                        stock_entry_detail = stock_entry.getone({'item_code': linked_item['item_code']})
                        
                        # Step 6: Deduct the qty from the existing quantity if the detail exists
                        if stock_entry_detail:
                            new_qty = stock_entry_detail.qty - qty_to_deduct
                            if new_qty < 0:
                                # Handle case where deduction exceeds current quantity
                                frappe.throw(f"Cannot deduct {qty} from {stock_entry_detail.qty}. Insufficient quantity.")
                            else:
                                stock_entry_detail.qty = new_qty
                                # Step 7: Save the updated Stock Entry document
                                stock_entry.save(ignore_permissions=True)

        # Step 8: Return True to indicate success
        return True