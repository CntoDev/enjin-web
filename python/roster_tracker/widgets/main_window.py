import sys
from PySide import QtGui


def get_application():
    return QtGui.QApplication(sys.argv)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, control):
        super(MainWindow, self).__init__()
        self._control = control
        
        self.setWindowTitle('CNTO Roster Manager')    
        self.create_menus()
        self.update_status_bar()
    
        self.update_button_states()
        
    def update_button_states(self):
        if self._control.database_loaded():
            self._load_action.setEnabled(False)
            self._export_action.setEnabled(True)
            self._scrape_action.setEnabled(True)
        else:
            self._load_action.setEnabled(True)
            self._export_action.setEnabled(False)
            self._scrape_action.setEnabled(False)
        
    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        
        self._load_action = QtGui.QAction('&Load database', self)
        self._load_action.triggered.connect(self.load_db_selected)
        self._file_menu.addAction(self._load_action)
        
        self._scrape_action = QtGui.QAction('&Scrape event', self)
        self._scrape_action.triggered.connect(self.scrape_event_selected)
        self._file_menu.addAction(self._scrape_action)
        
        self._export_action = QtGui.QAction('&Export data', self)
        self._export_action.triggered.connect(self.export_data)
        self._file_menu.addAction(self._export_action)
    
        self._file_menu.addSeparator()
    
        self._exit_action = QtGui.QAction('&Exit', self)
        self._exit_action.triggered.connect(self.close)
        self._file_menu.addAction(self._exit_action)
    
    def scrape_event_selected(self):
        pass
    
    def load_db_selected(self):
        self._control.set_database_directory(self.select_database_directory())
    
    def select_database_directory(self):
        selected_directory = QtGui.QFileDialog.getExistingDirectory()
        return selected_directory    
    
    def export_data(self):
        self.statusBar().showMessage("Load db")    
    
    def update_status_bar(self):
        if self._control.database_loaded():
            self.statusBar().showMessage("Ready")
        else:
            self.statusBar().showMessage("Still need database!")
        
    def start(self):
        self.show()
