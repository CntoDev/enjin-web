import time
import pickle
import os
from pyquery import PyQuery as pq
from selenium import webdriver
from datetime import datetime
from lxml import _elementpath as _dummy

class Attendance(object):
    def __init__(self, username_string, attending_string, note_string, role_string, attendance_report_timestamp):
        self.username = username_string
        self.attending_status = attending_string
        self.note = note_string
        self.role = role_string
        self.attendance_dt = attendance_report_timestamp

    def write_csv_row(self, output_file):
        output_file.write("%s,%s,%s,%s,%s\n" % (self.username, self.attending_status, self.note, self.role, self.attendance_dt.strftime("%Y-%m-%d %H:%M:%S")))

        
def enjin_dt_string_to_dt(date_string):
    date_string = date_string[5:].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
    dt = datetime.strptime(date_string, "%d %b %Y @ %H:%M:%S")
    return dt
    

def event_page_dt_string_to_dt(date_string):
    date_string = date_string.split(",")[1]
    dt = datetime.strptime(("%s " + date_string) % (datetime.now().year), "%Y %B %d")
    return dt

    
def get_attendance_for_user_id(browser, user_id):
    ac = webdriver.ActionChains(browser) 
    hover_element = browser.find_element_by_css_selector("[userid='%s'] .attending-type" % (user_id, ))
    ac.move_to_element(hover_element) 
    ac.perform()
    
    time.sleep(0.1)
    
    event_source = browser.page_source
    event_source = event_source.encode('utf-8')

    event_pq = pq(event_source)
    
    username_element = event_pq("[userid='%s'] .username .element_username" % (user_id,))[0]
    username_string = username_element.text
    
    attending_element = event_pq("[userid='%s'] .attending-type .text" % (user_id,))[0]
    attending_string = list(attending_element)[0].text
    
    note_element = event_pq("[userid='%s'] .note" % (user_id,))[0]
    note_string = note_element.text
    
    role_element = event_pq("[userid='%s'] .roles .role" % (user_id,))
    role_string = None
    if len(role_element) > 0:
        role_string = role_element[0].attrib["rolename"]
        
    attendance_history_element = event_pq('.history-attendance-items .item-history')[-1]
    attendance_type = attendance_history_element[0].text
    
    attendance_report_timestamp = attendance_history_element[1].text
    attendance_report_dt = enjin_dt_string_to_dt(attendance_report_timestamp)

    return Attendance(username_string, attending_string, note_string, role_string, attendance_report_dt)

    
def get_filename(start_dt):
    return start_dt.strftime("event-%Y-%m-%d.csv")
    
    
def get_event_start_dt(browser):
    event_source = browser.page_source
    event_source = event_source.encode('utf-8')
    
    event_pq = pq(event_source)
    start_element = event_pq(".item-event-start .info")
    start_text = start_element.text()
    return event_page_dt_string_to_dt(start_text)
    
    
def get_user_ids(browser):
    event_source = browser.page_source
    event_source = event_source.encode('utf-8')
    
    event_pq = pq(event_source)
    attend_list = event_pq(".attend-list")
    attend_items = attend_list(".scroller .item")
    
    user_ids = []
    for attend_item in attend_items:
        user_ids.append(attend_item.attrib["userid"])
        
    return user_ids

    
class Event(object):
    @classmethod
    def get_next_event(cls):
        browser = None
    
        if os.path.exists("home.html"):
            home_file = open("home.html", "r")
            home_source = "".join(home_file.readlines())
            home_file.close()
            
            home_pq = pq(home_source)
        else:
            if browser is None:
                browser = webdriver.Chrome()
        
            home_url = "http://carpenoctem.co/home"
            print "Retrieving home %s..." % (home_url, )
            browser.get(home_url)
            
            time.sleep(1.0)
            
            home_source = browser.page_source
            home_source = home_source.encode('utf-8')
            
            home_pq = pq(home_source)

            #home_file = open("home.html", "w")
            #home_file.write(home_source)
            #home_file.close()
        
        start_dt = None
        attendances = []
        
        try:
            events = home_pq('.event-info')
            assert len(events) > 0
            
            next_event = events[0]
            event_name = next_event[0].text
            event_url = "http://carpenoctem.co/" + next_event[0].attrib["href"]
            
            if os.path.exists("event.html"):
                event_file = open("event.html", "r")
                event_source = "".join(event_file.readlines())
                event_file.close()
            else:
                if browser is None:
                    browser = webdriver.Chrome()
            
                print "Retrieving next event %s..." % (event_url, )
                browser.get(event_url)
                
                time.sleep(1.0)
                
                start_dt = get_event_start_dt(browser)
                
                target_filename = get_filename(start_dt)
                if os.path.exists(target_filename):
                    os.remove(target_filename)
                    
                print "Found event for %s!" % (start_dt, )
                
                user_ids = get_user_ids(browser)
                print "Retrieving data for %s users..." % (len(user_ids), )
                
                for user_id in user_ids:
                    attendance = get_attendance_for_user_id(browser, user_id)
                    attendances.append(attendance)
                
                #event_file = open("event.html", "w")
                #event_file.write(event_source)
                #event_file.close()
            
        except Exception, e:
            print "Could not determine next event!"
            raise
          
        if browser is not None:
            browser.close()
        
        #pickle.dump( attendances, open( "save.p", "wb" ) )
        
        #os.remove("event.html")
        #os.remove("home.html")
        
        #attendances = pickle.load( open( "save.p", "rb" ) )
        
        return Event(start_dt, attendances)

    def __init__(self, start_dt, attendances):
        self.start_dt = start_dt
        self.attendances = attendances
        
    def write_roster_to_filename(self, output_filename):
        output_file = open(output_filename, "w")
        output_file.write("user,status,note,role,attendance_timestamp\n")
        for attendance in self.attendances:
            attendance.write_csv_row(output_file)
        output_file.close()
        
        print "Result written to %s!" % (output_filename,)
    
    def write_roster(self, output_dirname):
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)
        
        output_name = get_filename(self.start_dt)
        output_filename = os.path.join(output_dirname, output_name)
        try:
            self.write_roster_to_filename(output_filename)
        except IOError, e:
            self.write_roster_to_filename(output_filename + ".fallback")


if __name__ == "__main__":
    print "CNTO event tracker 0.1 by Supreme (sakkie99@gmail.com)"

    event = Event.get_next_event()
    
    event.write_roster("output")