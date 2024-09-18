from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelOrder(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_chief_for_menu()
        print("validate_s")
        frappe.publish_realtime('update_single_order', {
        'status': self.status
        })
        frappe.publish_progress(50,"my progress")

    def calculate_totals(self):
        total_qty = 0
        total = 0

        for item in self.get('hotel_items'):
            total_qty += item.qty
            total += item.amount

        self.total_qty = total_qty
        self.total = total

    def validate_chief_for_menu(self):
        for item in self.get('hotel_items'):
            is_prepared_by_employee = frappe.db.get_value('Menu', item.item_code, 'is_prepared_by_employee')
            frappe.log_error(f"Menu: {item.item_code}, Is Prepared By Employee: {is_prepared_by_employee}, Chief: {item.chief}", "Validation Debug")
            
            if is_prepared_by_employee and not item.chief:
                frappe.throw(f"Please put an employee name that must prepare the {item.item_code} you just put in the menu.")
            
            if not is_prepared_by_employee and item.chief:
                frappe.throw(f"Remove the employee name for the {item.item_code} because it is not marked as prepared by an employee.")


# @frappe.whitelist()
# def update_hotel_order_item_status(hotel_order_item_name, status):
#     frappe.db.set_value('Hotel Order Item', hotel_order_item_name, 'status', status)
#     frappe.db.commit()

#     frappe.publish_realtime(event='status_update', message={
#         'doctype': 'Hotel Order Item',
#         'docname': hotel_order_item_name,
#         'status': status
#     })

#     # Update the corresponding Single Order
#     hotel_order_item = frappe.get_doc('Hotel Order Item', hotel_order_item_name)
#     single_order_name = frappe.db.get_value('Single Order', {'source_docname': hotel_order_item_name}, 'name')
#     if single_order_name:
#         frappe.db.set_value('Single Order', single_order_name, 'status', status)
#         frappe.db.commit()

#         frappe.publish_realtime(event='status_update', message={
#             'doctype': 'Single Order',
#             'docname': single_order_name,
#             'status': status
#         })

#     return {'status': 'success', 'message': 'Status updated and broadcasted'}
