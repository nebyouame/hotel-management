frappe.listview_settings['Single Order'] = {
    onload: function(listview) {
        // Set route options to filter by status
        frappe.route_options = {
            "status": ['in', ['Pending', 'Delivered']]
        };

        // Specify the image field in your doctype (replace 'image' with the correct field name)
        // listview.image_field = 'image'; // Ensure this field exists in your doctype

        console.log("Image Field:", listview.image_field);
        // Use the onrender event to wait for the listview to fully render before switching the view
        listview.onrender = function() {
            // Check if the page has a set_view function and switch to image view
            if (listview.page && typeof listview.page.set_view === 'function') {
                listview.page.set_view('image'); // Switch to the Image view
            } else {
                console.error("set_view function is not available on the listview page");
            }
        };

        // Refresh the list view to apply the filter
        listview.refresh();
    }
};
