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
    attendance_report_timestamp = attendance_history_element[1].text[5:].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")

    attendance_report_dt = datetime.strptime(attendance_report_timestamp, "%d %b %Y @ %H:%M:%S")

    return Attendance(username_string, attending_string, note_string, role_string, attendance_report_dt)
        
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
        
        return Event(attendances)

    def __init__(self, attendances):
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
        
        output_name = "roster.csv"
        output_filename = os.path.join(output_dirname, output_name)
        try:
            self.write_roster_to_filename(output_filename)
        except IOError, e:
            self.write_roster_to_filename(output_filename + ".fallback")
          
if __name__ == "__main__":
    print "CNTO event tracker 0.1 by Supreme (sakkie99@gmail.com)"

    event = Event.get_next_event()
    
    event.write_roster("output")