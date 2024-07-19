import frappe
from frappe.model.document import Document

class SingleOrder(Document):
    pass

@frappe.whitelist()
def update_single_order_status(single_order_name, status):
    frappe.log_error(f"update_single_order_status called with {single_order_name} and {status}", "Workflow Debug")
    # Update Single Order status
    frappe.db.set_value('Single Order', single_order_name, 'status', status)
    frappe.db.commit()

    frappe.publish_realtime(event='status_update', message={
        'doctype': 'Single Order',
        'docname': single_order_name,
        'status': status
    })

    # Update the corresponding Hotel Order Item
    single_order = frappe.get_doc('Single Order', single_order_name)
    hotel_order_item_name = single_order.source_docname
    if hotel_order_item_name:
        frappe.db.set_value('Hotel Order Item', hotel_order_item_name, 'status', status)
        frappe.db.commit()

        frappe.publish_realtime(event='status_update', message={
            'doctype': 'Hotel Order Item',
            'docname': hotel_order_item_name,
            'status': status
        })

    return {'status': 'success', 'message': 'Status updated and broadcasted'}
