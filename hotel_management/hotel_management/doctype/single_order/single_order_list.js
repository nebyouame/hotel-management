frappe.listview_settings['Single Order'] = {
    onload: function(listview) {
        console.log("list") 
        // Set route options to filter status
        frappe.route_options = {
            "status": ['in', ['Pending', 'Accepted']]
        };
        // Refresh the list view to apply the filter
        listview.refresh();
        
        frappe.realtime.on('update_single_order', function(data) {
            console.log("listview.refresh();") 
            listview.refresh();
        });
    }
};



// frappe.listview_settings['Single Order'] = {
//     onload: function(listview) {
//         // Set route options to filter status
//         frappe.route_options = [
//             {"status": "pending"}
//         ]
//         // Refresh the list view to apply the filter
//         listview.refresh();
//     }
// };

