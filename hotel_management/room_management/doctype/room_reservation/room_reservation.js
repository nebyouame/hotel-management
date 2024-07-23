// Copyright (c) 2024, Powerware Tecnologies  and contributors
// For license information, please see license.txt

frappe.ui.form.on("Room Reservation", {
    onload: function (frm) {
        frm.set_query("room", "rooms_for_reservation",  function (doc, cdt, cdn) {
            lastRow =  locals[cdt][cdn];
            console.log("last roo ",lastRow)
            console.log(lastRow.ends_on != undefined ,lastRow.ends_on)
            var fromTop = doc.rooms_for_reservation.filter(r => (r.room != undefined && r.room != ""))
            var fromTop = doc.rooms_for_reservation.filter(r => ((r.starts_on >= lastRow.starts_on && r.starts_on <= lastRow.ends_on)  || (r.starts_on <= lastRow.starts_on && r.ends_on >= lastRow.ends_on) || (r.ends_on >= lastRow.starts_on && r.ends_on <= lastRow.ends_on) )).map(r => Number(r.room))
            let row = locals[cdt][cdn];
            var res =""
            
            console.log("fromTop",fromTop)
            console.log("windows",window.room)
            if(window.room)
                fromTop = fromTop.concat(window.room)
            fromTop = fromTop.filter((item, pos) => fromTop.indexOf(item) === pos)
            return {
                "filters": [
                    ["Room","type", "=", row.type],
                    ["Room","room_number", "not in", fromTop],
                ]
            };
        });
    }

});


frappe.ui.form.on('Reserved Room', {
    ends_on(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'room', "");
        lastRow = locals[cdt][cdn];
        if(lastRow.starts_on && lastRow.ends_on){
            if(new Date(lastRow.ends_on) < new Date(lastRow.starts_on)){
                frappe.model.set_value(cdt, cdn, 'ends_on', lastRow.starts_on);
                frappe.throw(__("From date can't be leasthan To date!"))
            }
            frappe.call({
        method: "hotel_management.room_management.doctype.util.get_Reservation_between_date",
        args: {
            starts_on: lastRow.starts_on,
            ends_on: lastRow.ends_on,
        },
        callback: function (r) {
            if (r.message) {
                res = r.message
                console.log("value ",res)
                window.room = res
            }
        }
    });}
    if(lastRow.starts_on && lastRow.ends_on){
        let Difference_In_Time = new Date(lastRow.ends_on).getTime() - new Date(lastRow.starts_on).getTime();
        let Difference_In_Days = Math.round(Difference_In_Time / (1000 * 3600 * 24));
        console.log("Difference_In_Days",Difference_In_Days)
        frappe.model.set_value(cdt, cdn, 'stay_days', Difference_In_Days +1);

    }
    },
    starts_on(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'room', "");
        lastRow = locals[cdt][cdn];
        if(lastRow.starts_on && lastRow.ends_on){
            if(new Date(lastRow.ends_on) < new Date(lastRow.starts_on)){
                frappe.model.set_value(cdt, cdn, 'ends_on', lastRow.starts_on);
                frappe.throw(__("From date can't be less than To date!"))
            }
            frappe.call({
                method: "hotel_management.room_management.doctype.util.get_Reservation_between_date",
                args: {
                    starts_on: lastRow.starts_on,
                    ends_on: lastRow.ends_on,
                },
                callback: function (r) {
                    if (r.message) {
                        res = r.message
                        console.log("value ",res)
                        window.room = res
                    }
                }
            });}
        if(lastRow.starts_on && lastRow.ends_on){
            let Difference_In_Time = new Date(lastRow.ends_on).getTime() - new Date(lastRow.starts_on).getTime();
            let Difference_In_Days = Math.round(Difference_In_Time / (1000 * 3600 * 24));
            frappe.model.set_value(cdt, cdn, 'stay_days', Difference_In_Days +1);
    
        }
    },

});
frappe.ui.form.on('Reserved Room', {
    type: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'room', "");
    },
    room: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.room !="")
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Room",
                name: row.room,
                fields: ['price'],
                limit: 1
            },
            callback(r) {
                if(r.message) {
                    frappe.model.set_value(cdt, cdn, 'price', r.message.price);
                }
            }
        });
    },
    price: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.price && row.stay_days)
            frappe.model.set_value(cdt, cdn, 'total_price', row.price*row.stay_days);
    },
    stay_days: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.price && row.stay_days)
            frappe.model.set_value(cdt, cdn, 'total_price', row.price*row.stay_days);
    },
    
});
