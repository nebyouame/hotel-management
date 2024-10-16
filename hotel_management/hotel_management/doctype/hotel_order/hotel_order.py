from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelOrder(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_chief_for_menu() # Call to update stock entries
        print("validate_s")
        frappe.publish_realtime('update_single_order', {
            'status': self.status
        })
        frappe.publish_progress(50, "my progress")

    def calculate_totals(self):
        total_qty = 0
        total = 0

        for item in self.get('hotel_items'):
            total_qty += item.qty
            total += item.amount

        total_vat = total - ((total * 0.15) / 1.15)

        self.total_qty = total_qty
        self.tot_vat = total
        self.total = total_vat

    def validate_chief_for_menu(self):
        for item in self.get('hotel_items'):
            is_prepared_by_employee = frappe.db.get_value('Menu', item.item_code, 'is_prepared_by_employee')
            frappe.log_error(f"Menu: {item.item_code}, Is Prepared By Employee: {is_prepared_by_employee}, Chief: {item.chief}", "Validation Debug")
            
            if is_prepared_by_employee and not item.chief:
                frappe.throw(f"Please put an employee name that must prepare the {item.item_code} you just put in the menu.")
            
            if not is_prepared_by_employee and item.chief:
                frappe.throw(f"Remove the employee name for the {item.item_code} because it is not marked as prepared by an employee.")
    
    