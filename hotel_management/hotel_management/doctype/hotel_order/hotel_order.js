frappe.ui.form.on('Hotel Order', {
    refresh: function(frm) {
        calculateTotals(frm);
        checkStatusForFSNumber(frm);
        toggleFields(frm); // Call to toggle fields based on status
    },
    hotel_items_add: function(frm) {
        calculateTotals(frm);
        checkStatusForFSNumber(frm);
        toggleFields(frm); // Call to toggle fields after adding an item
    },
    hotel_items_remove: function(frm) {
        calculateTotals(frm);
        checkStatusForFSNumber(frm);
        toggleFields(frm); // Call to toggle fields after removing an item
    },
    before_save: function(frm) {
        let today = new Date();
        let day = String(today.getDate()).padStart(2, '0');
        let month = String(today.getMonth() + 1).padStart(2, '0');
        let year = today.getFullYear();
        let formattedDate = year + '-' + month + '-' + day;

        frappe.model.set_value(frm.doctype, frm.docname, 'order_date', formattedDate);
        console.log('Order date set to:', formattedDate);

        // Check if fs_num is not empty and set status to 'Paid'
        if (frm.doc.fs_num) {
            frappe.model.set_value(frm.doctype, frm.docname, 'status', 'Paid');

            frm.doc.hotel_items.forEach(function(item) {
                if (item.status === 'Delivered') {
                    // Set the status to Paid if it is currently Delivered
                    frappe.model.set_value(item.doctype, item.name, 'status', 'Paid');
                }
            });
        }
        
        
    },
    after_save: function(frm) {
        console.log('Hotel Order saved');
        let assigned_users = [];

        if (frm.doc.hotel_items) {
            if (Array.isArray(frm.doc.hotel_items)) {
                
                let itemCodes = frm.doc.hotel_items.map(item => item.item_code);

                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Menu',
                        filters: { menu: ['in', itemCodes] },
                        fields: ['menu', 'image']
                    },
                    callback: function(menuResults) {
                        if (menuResults.message && menuResults.message.length > 0) {
                            let menuImages = {};
                            menuResults.message.forEach(function(menu) {
                                menuImages[menu.menu] = menu.image;
                            });

                            frm.doc.hotel_items.forEach(function(item) {
                                if (item.chief) {
                                    assigned_users.push({
                                        user: item.chief,
                                        item_code: item.item_code,
                                        item_name: item.item_name,
                                        qty: item.qty,
                                        name: item.name,
                                        image: menuImages[item.item_code] || null 
                                    });
                                }
                            });

                            assigned_users.forEach(function(user) {
                                frappe.call({
                                    method: 'frappe.client.get_list',
                                    args: {
                                        doctype: 'Single Order',
                                        filters: {
                                            menu: user.item_code,
                                            table_number: frm.doc.table_order_no,
                                            waiter: frm.doc.waiter,
                                            assigned_chief: user.user,
                                            source_docname: user.name
                                        },
                                        fields: ['name']
                                    },
                                    callback: function(r) {
                                        if (r.message.length === 0) {
                                            frappe.call({
                                                method: 'frappe.client.insert',
                                                args: {
                                                    doc: {
                                                        doctype: 'Single Order',
                                                        menu: user.item_code,
                                                        table_number: frm.doc.table_order_no,
                                                        waiter: frm.doc.waiter,
                                                        quantity: user.qty,
                                                        assigned_chief: user.user,
                                                        status: 'Pending',
                                                        source_docname: user.name,
                                                        order_num: frm.doc.name,
                                                        image: user.image 
                                                    }
                                                },
                                                callback: function(r) {
                                                    if (!r.exc) {
                                                        frappe.show_alert({
                                                            message: __('Single Order created for {0} with item_code {1} and quantity {2}', [user.user, user.item_code, user.qty]),
                                                            indicator: 'green',
                                                            persist: true
                                                        });

                                                        frappe.call({
                                                            method: 'frappe.share.add',
                                                            args: {
                                                                doctype: 'Single Order',
                                                                name: r.message.name,
                                                                user: user.user,
                                                                read: 1,
                                                                write: 1,
                                                                share: 0,
                                                                everyone: 0,
                                                                notify: 1
                                                            },
                                                            callback: function(share_res) {
                                                                if (!share_res.exc) {
                                                                    console.log('Shared Single Order with user:', user.user);
                                                                } else {
                                                                    frappe.msgprint(__('Error sharing Single Order with {0}: {1}', [user.user, share_res.exc]));
                                                                }
                                                            }
                                                        });

                                                    } else {
                                                        frappe.msgprint(__('Error creating Single Order for {0}: {1}', [user.user, r.exc]));
                                                    }
                                                }
                                            });
                                        } else {
                                            console.log('Single Order already exists for', user.item_code, 'assigned to', user.user);
                                        }
                                    }
                                });
                            });
                        } else {
                            console.log('No menu images found');
                        }
                    }
                });
            } else {
                console.log('hotel_items is not an array, it is a', typeof frm.doc.hotel_items);
            }
        } else {
            console.log('hotel_items field is undefined or null');
        }

        frappe.realtime.publish('update_single_order', {
            'hotel_order_name': frm.doc.name,
            'status': frm.doc.status
        });
    }
});

frappe.ui.form.on('Hotel Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, 'qty', 1);

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Menu',
                filters: { menu: row.item_code },
                fields: ['rate'],
                limit: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let rate = r.message[0].rate;
                    frappe.model.set_value(cdt, cdn, 'rate', rate);
                    let amount = row.qty * rate;
                    frappe.model.set_value(cdt, cdn, 'amount', amount);
                    let rate_vat = (rate - ((rate * 0.15) / 1.15));
                    frappe.model.set_value(cdt, cdn, 'rate_vat', rate_vat);
                } else {
                    frappe.model.set_value(cdt, cdn, 'rate', 0);
                    frappe.model.set_value(cdt, cdn, 'amount', 0);
                }
            }
        });
    },
    qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let amount = row.qty * row.rate;
        frappe.model.set_value(cdt, cdn, 'amount', amount);
    },
    status: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.status === 'Cancelled') {
            frappe.model.set_value(cdt, cdn, 'rate', 0);
            frappe.model.set_value(cdt, cdn, 'amount', 0);

            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Single Order',
                    filters: {
                        menu: row.item_code,
                        table_number: frm.doc.table_order_no,
                        waiter: frm.doc.waiter,
                        assigned_chief: row.chief,
                        source_docname: row.name
                    },
                    fields: ['name']
                },
                callback: function(r) {
                    if (r.message.length > 0) {
                        let single_order_name = r.message[0].name;

                        frappe.call({
                            method: 'frappe.client.set_value',
                            args: {
                                doctype: 'Single Order',
                                name: single_order_name,
                                fieldname: 'status',
                                value: 'Cancelled'
                            },
                            callback: function(r) {
                                if (!r.exc) {
                                    frappe.show_alert({
                                        message: __('Single Order {0} status changed to Cancelled', [single_order_name]),
                                        indicator: 'red',
                                        persist: true
                                    });
                                } else {
                                    frappe.msgprint(__('Error updating Single Order status to Cancelled: {0}', [r.exc]));
                                }
                            }
                        });
                    } else {
                        console.log('No Single Order found for item code:', row.item_code, 'assigned to', row.chief);
                    }
                }
            });
        }

        checkStatusForFSNumber(frm);
        toggleFields(frm); // Check and toggle fields after status change
    }
});

// Function to toggle fields based on the status
function toggleFields(frm) {
    frm.doc.hotel_items.forEach(function(item) {
        let isEditable = item.status === 'Pending'; // Allow editing only if status is Pending
        frappe.get_meta('Hotel Order Item').fields.forEach(function(field) {
            // Lock all fields, including status
            frm.set_df_property(field.fieldname, 'read_only', !isEditable, item.name);
        });
    });
}

function checkStatusForFSNumber(frm) {
    let has_delivered = false;
    let has_cancelled = false;
    let has_pending_or_accepted = false;

    frm.doc.hotel_items.forEach(function(item) {
        if (item.status === "Delivered") {
            has_delivered = true;
        }
        if (item.status === "Cancelled") {
            has_cancelled = true;
        }
        if (item.status === "Pending" || item.status === "Accepted") {
            has_pending_or_accepted = true;
        }
    });

    // Check if form status is 'Paid'
    const isPaid = frm.doc.status === 'Paid';

    // Show FS Number if the form status is 'Paid'
    // or if there are delivered items, no pending/accepted, and not all items are cancelled
    const showFSNumber = isPaid || (has_delivered && !has_pending_or_accepted);

    frm.toggle_display('fs_num', showFSNumber);
}

function calculateTotals(frm) {
    let total_qty = 0;
    let total = 0;
    let total_vat = 0;

    frm.doc.hotel_items.forEach(function(item) {
        total_qty += item.qty;
        total += item.amount;
    });

    total_vat = total - ((total * 0.15) / 1.15);

    frappe.model.set_value(frm.doctype, frm.docname, 'total_qty', total_qty);
    frappe.model.set_value(frm.doctype, frm.docname, 'tot_vat', total);
    frappe.model.set_value(frm.doctype, frm.docname, 'total', total_vat);
}

// Real-time updates handler
frappe.realtime.on('update_single_order', function(data) {
    frappe.call({
        method: 'frappe.client.set_value',
        args: {
            doctype: 'Single Order',
            name: data.hotel_order_name,
            fieldname: 'status',
            value: data.status
        },
        callback: function(r) {
            if (!r.exc) {
                frappe.show_alert({
                    message: __('Single Order {0} status updated to {1}', [data.hotel_order_name, data.status]),
                    indicator: 'blue',
                    persist: true
                });
            }
        }
    });
});
