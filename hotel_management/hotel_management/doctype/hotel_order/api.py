
from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def update_stock_entry_qty(menu_name, qty):
        qty_to_deduct = float(qty) 
       
        items_linked_to_menu = frappe.get_list('Item', 
                                               filters={'menuu': menu_name},
                                               fields=['name', 'item_code'])

        if items_linked_to_menu:
         
            for linked_item in items_linked_to_menu:
               
                stock_entries = frappe.get_list('Stock Entry Detail', 
                                                filters={'item_code': linked_item['item_code']},
                                                fields=['parent', 'name', 'qty'])

                if stock_entries:
                    for entry in stock_entries:
                       
                        stock_entry = frappe.get_doc('Stock Entry', entry['parent'])
                        
                        
                        stock_entry_detail = stock_entry.getone({'item_code': linked_item['item_code']})
                        
                        
                        if stock_entry_detail:
                            new_qty = stock_entry_detail.qty - qty_to_deduct
                            if new_qty < 0:
                            
                                frappe.throw(f"Cannot deduct {qty} from {stock_entry_detail.qty}. Insufficient quantity.")
                            else:
                                stock_entry_detail.qty = new_qty
                                
                                stock_entry.save(ignore_permissions=True)

                    return True 
        return False