frappe.ui.form.on('Hotel Order', {
    refresh: function(frm) {
        calculateTotals(frm);
    },
    hotel_items_add: function(frm) {
        calculateTotals(frm);
    },
    hotel_items_remove: function(frm) {
        calculateTotals(frm);
    },
    before_save: function(frm) {
        let today = new Date();
        let day = String(today.getDate()).padStart(2, '0');
        let month = String(today.getMonth() + 1).padStart(2, '0');
        let year = today.getFullYear();
        let formattedDate = year + '-' + month + '-' + day;

        frappe.model.set_value(frm.doctype, frm.docname, 'order_date', formattedDate);
        console.log('Order date set to:', formattedDate);
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
                        doctype: 'Item',
                        filters: { name: ['in', itemCodes] },
                        fields: ['name', 'image']
                    },
                    callback: function(itemResults) {
                        if (itemResults.message && itemResults.message.length > 0) {
                            let itemImages = {};
                            itemResults.message.forEach(function(item) {
                                itemImages[item.name] = item.image;
                            });

                            frm.doc.hotel_items.forEach(function(item) {
                                if (item.chief) {
                                    assigned_users.push({
                                        user: item.chief,
                                        item_code: item.item_code,
                                        item_name: item.item_name,
                                        qty: item.qty,
                                        name: item.name,
                                        image: itemImages[item.item_code] || null 
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
                            console.log('No item images found');
                        }
                    }
                });
            } else {
                console.log('hotel_items is not an array, it is a', typeof frm.doc.hotel_items);
            }
        } else {
            console.log('hotel_items field is undefined or null');
        }
    }
});

frappe.ui.form.on('Hotel Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, 'qty', 1);

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Item Price',
                filters: { item_code: row.item_code },
                fields: ['price_list_rate'],
                limit: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let rate = r.message[0].price_list_rate;
                    frappe.model.set_value(cdt, cdn, 'rate', rate);
                    let amount = row.qty * rate;
                    frappe.model.set_value(cdt, cdn, 'amount', amount);
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
    }
});

function calculateTotals(frm) {
    let total_qty = 0;
    let total = 0;

    frm.doc.hotel_items.forEach(function(item) {
        total_qty += item.qty;
        total += item.amount;
    });

    frappe.model.set_value(frm.doctype, frm.docname, 'total_qty', total_qty);
    frappe.model.set_value(frm.doctype, frm.docname, 'total', total);
}

// Real-time updates handler
frappe.realtime.on('status_update', (data) => {
    if (cur_frm.doc.doctype === 'Hotel Order') {
        if (data.doctype === 'Hotel Order Item') {
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
    } else if (cur_frm.doc.doctype === 'Single Order') {
        if (data.doctype === 'Single Order') {
            let single_order = cur_frm.doc;
            if (single_order.name === data.docname) {
                single_order.status = data.status;
                cur_frm.refresh_field('status');
                frappe.show_alert({
                    message: __('Single Order status updated to {0}', [data.status]),
                    indicator: 'green',
                    persist: true
                });
            }
        }
    }
});
