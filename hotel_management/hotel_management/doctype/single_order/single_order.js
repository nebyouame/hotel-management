frappe.ui.form.on('Single Order', {
    status: function(frm) {
        updateSingleOrderStatus(frm);
    },
    workflow_state: function(frm) {
        updateSingleOrderStatus(frm);
    },
    after_workflow_action: function(frm) {
        updateSingleOrderStatus(frm);
    }
});

function updateSingleOrderStatus(frm) {
    console.log('Updating status for:', frm.doc.name, 'to:', frm.doc.workflow_state || frm.doc.status);
    
    frappe.call({
        method: 'hotel_management.hotel_management.doctype.single_order.single_order.update_single_order_status',
        args: {
            single_order_name: frm.doc.name,
            status: frm.doc.workflow_state || frm.doc.status
        },
        callback: function(r) {
            if (!r.exc) {
                frappe.show_alert({
                    message: __('Hotel Order Item status updated to {0}', [frm.doc.workflow_state || frm.doc.status]),
                    indicator: 'green',
                    persist: true
                });
                console.log('Server-side status update successful');
            } else {
                frappe.msgprint(__('Error updating Hotel Order Item status: {0}', [r.exc]));
                console.error('Server-side status update failed', r.exc);
            }
        }
    });
}

// Real-time updates handler
frappe.realtime.on('status_update', (data) => {
    console.log('Real-time update received:', data);
    if (data.doctype === 'Single Order') {
        if (cur_frm.doc.doctype === 'Single Order' && cur_frm.doc.name === data.docname) {
            cur_frm.set_value('status', data.status);
            cur_frm.refresh_field('status');
            frappe.show_alert({
                message: __('Single Order status updated to {0}', [data.status]),
                indicator: 'green',
                persist: true
            });
        }
    } else if (data.doctype === 'Hotel Order Item') {
        if (cur_frm.doc.doctype === 'Hotel Order') {
            let hotel_order_item = cur_frm.doc.hotel_items.find(i => i.name === data.docname);
            if (hotel_order_item) {
                hotel_order_item.status = data.status;
                cur_frm.refresh_field('hotel_items');
                frappe.show_alert({
                    message: __('Hotel Order Item status updated to {0}', [data.status]),
                    indicator: 'green',
                    persist: true
                });
            }
        }
    }
});
