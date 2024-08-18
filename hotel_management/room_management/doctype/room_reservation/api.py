
from datetime import datetime
import json
import frappe
import pytz


@frappe.whitelist()
def calculatePenalty(rooms):
    penalty_obj = {}
    json_object = json.loads(rooms)
    settings = frappe.get_doc('Room Reservation Settings')
    for room in json_object:
        if room['ends_on']:
            roomCheck = frappe.get_all('Reserved Room', filters={'name': room['name']},  # Filter by 'name'
            fields=['*'],)
            if(not len(roomCheck)):
                continue
            # print("room: ",room)
            if room["status"] == "Check-out":
                continue
            ends_on = datetime.strptime(room['ends_on'], '%Y-%m-%d').date()
            today = datetime.today().date()
            print(ends_on)
            print(datetime.today().date())
            print(ends_on < today)
            print(settings.enable_late_check_out_penalty)
            if(ends_on < today  and settings.enable_late_check_out_penalty):
                timezone = pytz.timezone('Etc/GMT-3')
                check_out_time = datetime.strptime(settings.check_out_time, '%H:%M:%S').time()
                current_time =  datetime.now(timezone).time()
                # print("check_out_time: ",check_out_time)
                # print("current_time: ",current_time)
                if current_time > check_out_time:
                    reservation = frappe.get_doc('Reserved Room', room['name'])
                    very_late_check_out_penalty_time =  datetime.strptime(settings.very_late_check_out_time, '%H:%M:%S').time()
                    if settings.enable_very_late_check_out_penalty and current_time > very_late_check_out_penalty_time:
                        if settings.very_late_check_out_penalty == "Half price of the room":
                            frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price']/2)
                            penalty_obj[room['name']] = room['price']/2
                        else:
                            frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price'])
                            penalty_obj[room['name']] = room['price']
                        continue
                    if settings.late_check_out_penalty == "Half price of the room":
                        frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price']/2)
                        penalty_obj[room['name']] = room['price']/2
                    else:
                        frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price'])
                        penalty_obj[room['name']] = room['price']
                    if settings.late_check_out_penalty == "Half price of the room":
                        frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price']/2)
                        penalty_obj[room['name']] = room['price']/2
                    else:
                        frappe.db.set_value('Reserved Room', room['name'], 'penalty', room['price'])
                        penalty_obj[room['name']] = room['price']

    print("penalty: ",rooms)
    return penalty_obj