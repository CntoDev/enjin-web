import time
import traceback
import logging
import pickle
import os
from pyquery import PyQuery as pq
from selenium import webdriver
from datetime import datetime
from lxml import _elementpath as _dummy

log = logging.getLogger("event-tracker")
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

fh = logging.FileHandler("event-tracker.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

browser = webdriver.Chrome()
#browser = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)

class Attendance(object):
    def __init__(self, username_string, attending_string, role_string):
        self.username = username_string
        self.attending_status = attending_string
        self.role = role_string

    def write_csv_row(self, output_file):
        output_file.write("%s,%s,%s\n" % (self.username, self.attending_status, self.role))

        
def enjin_dt_string_to_dt(date_string):
    date_string = date_string[5:].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")
    dt = datetime.strptime(date_string, "%d %b %Y @ %H:%M:%S")
    return dt
    

def event_page_dt_string_to_dt(date_string):
    date_string = date_string.split(",")[1]
    
    dt = None
    
    try:
      dt = datetime.strptime(("%s " + date_string) % (datetime.now().year), "%Y %B %d")
    except Exception, e:
      print e
      
    try:
      dt = datetime.strptime(("%s " + date_string) % (datetime.now().year), "%Y  %b %d")
    except Exception, e:
      print e
      
    return dt

    
def get_attendance_for_user_id(browser, user_id):
    #ac = webdriver.ActionChains(browser) 
    #hover_element = browser.find_element_by_css_selector("[userid='%s'] .attending-type" % (user_id, ))
    #ac.move_to_element(hover_element) 
    #ac.perform()
    
    #time.sleep(0.1)
    
    event_source = browser.page_source
    event_source = event_source.encode('utf-8')

    event_pq = pq(event_source)
    
    username_element = event_pq("[userid='%s'] .username .element_username" % (user_id,))[0]
    username_string = username_element.text
    
    attending_element = event_pq("[userid='%s'] .attending-type .text" % (user_id,))[0]
    attending_string = list(attending_element)[0].text
    if attending_string is None:
        attending_string = ""
    
    #note_element = event_pq("[userid='%s'] .note" % (user_id,))[0]
    #note_string = note_element.text
    
    role_element = event_pq("[userid='%s'] .roles .role" % (user_id,))
    role_string = ""
    if len(role_element) > 0:
        role_string = role_element[0].attrib["rolename"]
        
    #attendance_history_element = event_pq('.history-attendance-items .item-history')[-1]
    #attendance_type = attendance_history_element[0].text
    
    #attendance_report_timestamp = attendance_history_element[1].text
    #attendance_report_dt = enjin_dt_string_to_dt(attendance_report_timestamp)

    return Attendance(username_string, attending_string, role_string)

    
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
        """Unfortunately, have to use selenium to retrieve the pages, since there is
        extensive DDoS protection on enjin.  Simply using requests was quickly blocked.
        """
        home_url = "http://carpenoctem.co/home"
        log.info("Retrieving home %s..." % (home_url, ))
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
            
            log.info("Retrieving next event %s..." % (event_url, ))
            browser.get(event_url)
            
            time.sleep(1.0)
            
            start_dt = get_event_start_dt(browser)
            
            target_filename = get_filename(start_dt)
            if os.path.exists(target_filename):
                os.remove(target_filename)
                
            log.info("Found event for %s!" % (start_dt, ))
            
            user_ids = get_user_ids(browser)
            log.info("Retrieving data for %s users..." % (len(user_ids), ))
            
            for user_id in user_ids:
                attendance = get_attendance_for_user_id(browser, user_id)
                attendances.append(attendance)
            
            #event_file = open("event.html", "w")
            #event_file.write(event_source)
            #event_file.close()
            
        except Exception, e:
            log.info("Could not determine next event!")
            raise
          
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
        #output_file.write("user,status,role\n")
        self.attendances.sort(key=lambda x: x.username)
        
        for attendance in self.attendances:
            attendance.write_csv_row(output_file)
        output_file.close()
        
        log.info("Result written to %s!" % (output_filename,))
    
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
    log.info("CNTO event tracker 0.1.2 by Supreme (sakkie99@gmail.com)")
    log.info("Starting roster retrieval...")

    try:
      if browser is None:
        raise Exception("Could not create instance of browser!")
    
      event = Event.get_next_event()
      
      event.write_roster("output")
      
      log.info("Roster retrieval for event on %s complete!" % (event.start_dt.strftime("%Y-%m-%d"), ))
    except Exception, e:
      log.error(traceback.format_exc())
      
    if browser is not None:
      browser.close()
        
