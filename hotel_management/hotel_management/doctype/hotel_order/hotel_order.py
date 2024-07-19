from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelOrder(Document):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        total_qty = 0
        total = 0

        for item in self.get('hotel_items'):
            total_qty += item.qty
            total += item.amount

        self.total_qty = total_qty
        self.total = total


@frappe.whitelist()
def update_hotel_order_item_status(hotel_order_item_name, status):
    frappe.db.set_value('Hotel Order Item', hotel_order_item_name, 'status', status)
    frappe.db.commit()

    frappe.publish_realtime(event='status_update', message={
        'doctype': 'Hotel Order Item',
        'docname': hotel_order_item_name,
        'status': status
    })

    # Update the corresponding Single Order
    hotel_order_item = frappe.get_doc('Hotel Order Item', hotel_order_item_name)
    single_order_name = frappe.db.get_value('Single Order', {'source_docname': hotel_order_item_name}, 'name')
    if single_order_name:
        frappe.db.set_value('Single Order', single_order_name, 'status', status)
        frappe.db.commit()

        frappe.publish_realtime(event='status_update', message={
            'doctype': 'Single Order',
            'docname': single_order_name,
            'status': status
        })

    return {'status': 'success', 'message': 'Status updated and broadcasted'}
