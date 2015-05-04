from multiprocessing.managers import SyncManager
from multiprocessing.process import Process
import requests
import time

def get_page_data(url, return_dict):
    r = requests.get(url)
    return_dict['page'] = r.text


class Downloader(object):
    def __init__(self, timeout=30, retries=100, wait=1):
        self.timeout = timeout
        self.retries = retries
        self.wait = wait
        
        self.manager = SyncManager()
        self.manager.start()
        
    def retry_fetch_data(self, url):
        market_data = self.fetch_data(url)
        
        retries = 1
        while not market_data and retries < self.retries:
            print "Retry #%s..." % str(retries)
            market_data = self.fetch_data(url)
            if market_data:
                print "Fetched: " + str(len(market_data))
            else:
                print "Fetched nothing!"
            retries += 1
        
        return market_data
    
    def fetch_data(self, url):
        limit = 60
        msg = "Downloading " + url[0: min(limit, len(url))] 
        if len(url) > limit:
            msg += "(+" + str(len(url) - limit) + ")"
        print msg
            
        return_dict = self.manager.dict()
        self.job = Process(target=get_page_data, args=(url, return_dict))
        self.job.start()
        
        self.job.join(self.timeout)
        if self.job.is_alive():
            self.job.terminate()
        self.job = None
        
        market_data = None
        if 'page' in return_dict:
            market_data = return_dict['page']
        
        if self.wait > 0:
            time.sleep(self.wait)
        
        return market_data