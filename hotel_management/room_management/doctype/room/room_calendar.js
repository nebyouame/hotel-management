
frappe.views.calendar['Room'] = {
    field_map: {
        start: 'starts_on',
        end: 'ends_on',
        id: 'title',
        allDay: 'all_day',
        title: 'title'
        // status: 'event_type',
        // color: 'color'
    },
    // style_map: {
    //     Public: 'success',
    //     Private: 'info'
    // },
    order_by: 'room',
    get_events_method: 'hotel_management.room_management.doctype.util.get_Reservation'
}
