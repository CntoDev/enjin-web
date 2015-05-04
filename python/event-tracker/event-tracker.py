import multiprocessing
from downloader import Downloader
from pyquery import PyQuery as pq

class Event(object):
    @classmethod
    def get_next_event(cls):
        d = Downloader(wait=0.0)
        page_string = d.retry_fetch_data("http://carpenoctem.co/")
        
        print page_string
        
        page = pq(page_string)
        
        print page
        
        return Event()

    def write_roster(self, output_filename):
        pass
        
if __name__ == "__main__":
    event = Event.get_next_event()
    
    event.write_roster("roster.txt")