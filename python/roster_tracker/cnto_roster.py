import os
import sys

from roster_db import RosterDatabase
from config_file import ConfigFile
from widgets.main_window import MainWindow, get_application


class RosterViewer(object):
    def __init__(self):
        self._app = get_application()
        self._db = None
        self._config = ConfigFile(os.path.join(os.path.dirname(__file__), "config.xml"))
        if self._config.last_loaded_dir is not None:
            self.set_database_directory(self._config.last_loaded_dir)
        
    def run(self):
        self._mainWin = MainWindow(self)
        self._mainWin.start()
        
        return_value = self._app.exec_()
        
        self._config.write()
        
        return return_value

    def database_loaded(self):
        return self._db is not None
    
    def set_database_directory(self, directory):
        print "Set db directory to %s" % (directory, )
        try:
            self._db = RosterDatabase(directory)
            print "DB loaded from %s!" % (directory, )
            self._config.last_loaded_dir = directory
        except Exception, e:
            print e
            self._db = None
            self._config.last_loaded_dir = None
        
if __name__ == "__main__":
    app = RosterViewer()
    sys.exit(app.run())