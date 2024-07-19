// Copyright (c) 2024, Powerware Tecnologies  and contributors
// For license information, please see license.txt

frappe.ui.form.on("Room Reservation", {
    onload: function (frm) {
        frm.set_query("room", "rooms_for_reservation",  function (doc, cdt, cdn) {
            lastRow =  locals[cdt][cdn];
            console.log("last roo ",lastRow)
            console.log(lastRow.ends_on != undefined ,lastRow.ends_on)
            var fromTop = doc.rooms_for_reservation.filter(r => (r.room != undefined && r.room != "")).map(r => Number(r.room))
            let row = locals[cdt][cdn];
            var res =""
            
            console.log("windows",window.room)
            if(window.room)
                fromTop = fromTop.concat(window.room)
            return {
                // query: "hotel_management.room_management.doctype.util.get_Reservation_between_date",
                // "filters": {
                //     "type": row.type,
                //     "fromTop": fromTop,
                //     "ends_on": lastRow.ends_on,
                //     "starts_on": lastRow.starts_on,

                // }
                "filters": [
                    ["Room","type", "=", row.type],
                    ["Room","room_number", "not in", fromTop],
                ]
            };
        });
        // if(lastRow.ends_on != undefined)
        // frappe.call({
        //     method: "hotel_management.room_management.doctype.util.get_Reservation_between_date",
        //     args: {
        //         starts_on: lastRow.starts_on,
        //         ends_on: lastRow.ends_on,
        //     },
        //     callback: function (r) {
        //         if (r.message) {
                    
        //         }
        //         // frm.set_value('status',r['message'])
        //     }
        // });



    }
    // refresh(frm) {
    //     console.log(frm.doc.rooms_for_reservation)
    //     frm.set_query("room", "rooms_for_reservation", function (doc, cdt, cdn) {
    //         return {
    //           "filters": [
    //             ["Room","status", "=", "Unreserved"]
    //         ]
    //     }
    //       });
    // },

});


frappe.ui.form.on('Reserved Room', { // The child table is defined in a DoctType called "Dynamic Link"
    ends_on(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
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
            // frm.set_value('status',r['message'])
        }
    });}
    if(lastRow.starts_on && lastRow.ends_on){
        let Difference_In_Time = new Date(lastRow.ends_on).getTime() - new Date(lastRow.starts_on).getTime();
        let Difference_In_Days = Math.round(Difference_In_Time / (1000 * 3600 * 24));
        console.log("Difference_In_Days",Difference_In_Days)
        frappe.model.set_value(cdt, cdn, 'stay_days', Difference_In_Days +1);

    }
    },
    starts_on(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
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
                    // frm.set_value('status',r['message'])
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
        // console.log("room add ", frm.doc)
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
    // type(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
    //     // frm: current ToDo form
    //     // cdt: child DocType 'Dynamic Link'
    //     // cdn: child docname (something like 'a6dfk76')
    //     // cdt and cdn are useful for identifying which row triggered this event
    //     var array = frm.doc.rooms_for_reservation.filter(r =>(r.room != undefined && r.room != "")).map(r =>  Number(r.room))
    //     var type = frm.doc.rooms_for_reservation.filter(r =>(r.name == cdn)).map(r =>  r.type)[0]
    //     console.log(cdn)
    //     console.log(type)

    //     // frappe.msgprint('A row has been added to the links table 🎉 ');
    //     frm.set_query("room", "rooms_for_reservation", function (doc, cdt, cdn) {
    //         console.log("doc ",doc)
    //         return {
    //           "filters": [
    //             ["Room","status", "=", "reserved"],
    //             ["Room","type", "!=", type],
    //             ["Room","room_number", "not in", array],
    //         ]
    //     }
    //       });
    // },

});
