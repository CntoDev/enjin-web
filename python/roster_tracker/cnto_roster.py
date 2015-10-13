import os
import sys

from datetime import datetime
from roster_db import RosterDatabase
from config_file import ConfigFile
from widgets.main_window import MainWindow, get_application
from roster_tracker import ScrapeThread


class RosterViewer(object):
    def __init__(self):
        self._app = get_application()
        self._db = None
        self._viewer = None
        self._config = ConfigFile(os.path.join(os.path.dirname(__file__), "config.xml"))
        if self._config.last_loaded_dir is not None:
            self.set_database_directory(self._config.last_loaded_dir)
        
    def run(self):
        self._viewer = MainWindow(self)
        self._viewer.start()
        
        return_value = self._app.exec_()
        
        self._config.write()
        
        return return_value

    def scraped_result(self, event_date, result):
        self._db.insert_attendances(event_date, result)

    def scrape(self, dt, start_hour, end_hour):
        start_dt = datetime(dt.year, dt.month, dt.day, start_hour, 0, 0)
        end_dt = datetime(dt.year, dt.month, dt.day, end_hour, 0, 0)
        
        scrape_thread = ScrapeThread(self._viewer, start_dt, end_dt)
        scrape_thread.start()

    def database_loaded(self):
        return self._db is not None
    
    def set_database_directory(self, directory):
        print "Set db directory to %s" % (directory,)
        if directory is not None:
            try:
                self._db = RosterDatabase(directory, strict=True)
                print "DB loaded from %s!" % (directory,)
                self._config.last_loaded_dir = directory
            except Exception, e:
                self._viewer.show_message("Error", "Could not read database!")
                self._db = None
                self._config.last_loaded_dir = None
        else:
            self._config.last_loaded_dir = None
            self._db = None
        
        if self._viewer is not None:
            self._viewer.update_button_states()
        
if __name__ == "__main__":
    app = RosterViewer()
    sys.exit(app.run())
