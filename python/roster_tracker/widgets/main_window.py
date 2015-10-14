import sys
from PySide import QtGui, QtCore
from scrape_event import ScrapeEventWidget
from export_data import ExportDataWidget


def get_application():
    return QtGui.QApplication(sys.argv)


class MainWindow(QtGui.QMainWindow):
    busy_signal = QtCore.Signal(object)
    show_message_signal = QtCore.Signal(object, object)
    scraped_result_signal = QtCore.Signal(object, object)
    
    def __init__(self, control):
        super(MainWindow, self).__init__()
        self._control = control
        
        self.busy_signal.connect(self.show_busy)
        self.show_message_signal.connect(self.show_message)
        self.scraped_result_signal.connect(self.scraped_result)
        
        self.setWindowTitle('CNTO Roster Manager')    
        self.create_menus()
        self.update_status_bar()
    
        self.update_button_states()
        
        self.resize(600, 400)
    
    @QtCore.Slot(object, object)
    def scraped_result(self, event_date, result):
        self._control.scraped_result(event_date, result)
    
    @QtCore.Slot(object, object)
    def show_message(self, header, message):
        
        flags = QtGui.QMessageBox.StandardButton.Ok
        response = QtGui.QMessageBox.warning(self, header,
                                             message, flags)
    
    @QtCore.Slot(object, object)
    def ask_yes_no_question(self, header, question):
        
        flags = QtGui.QMessageBox.StandardButton.Yes
        flags |= QtGui.QMessageBox.StandardButton.No
        response = QtGui.QMessageBox.question(self, header,
                                              question, flags)
        if response == QtGui.QMessageBox.StandardButton.Yes:
            return True
        else:
            return False
    
    def update_button_states(self):
        if self._control.database_loaded():
            self._load_action.setEnabled(False)
            self._export_action.setEnabled(True)
            self._scrape_action.setEnabled(True)
            self._unload_action.setEnabled(True)
        else:
            self._load_action.setEnabled(True)
            self._export_action.setEnabled(False)
            self._scrape_action.setEnabled(False)
            self._unload_action.setEnabled(False)
        
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
    
        self._unload_action = QtGui.QAction('&Unload data', self)
        self._unload_action.triggered.connect(self.unload_db)
        self._file_menu.addAction(self._unload_action)
    
        self._file_menu.addSeparator()
    
        self._exit_action = QtGui.QAction('&Exit', self)
        self._exit_action.triggered.connect(self.close)
        self._file_menu.addAction(self._exit_action)
    
    @QtCore.Slot(object)
    def show_busy(self, busy):
        if busy:
            if self.centralWidget() is not None:
                self.centralWidget().setEnabled(False)
        else:
            if self.centralWidget() is not None:
                self.centralWidget().refresh()
                self.centralWidget().setEnabled(True)
            
    
    def unload_db(self):
        self._control.set_database_directory(None)
        self.setCentralWidget(None)
    
    def scrape(self, dt, start_hour, end_hour):
        self._control.scrape(dt, start_hour, end_hour)
    
    def scrape_event_selected(self):
        self.setCentralWidget(ScrapeEventWidget(self))
    
    def load_db_selected(self):
        self._control.set_database_directory(self.select_database_directory())
    
    def select_database_directory(self):
        selected_directory = QtGui.QFileDialog.getExistingDirectory()
        return selected_directory    
    
    def export_data(self):
        self.setCentralWidget(ExportDataWidget(self))    
    
    def update_status_bar(self):
        if self._control.database_loaded():
            self.statusBar().showMessage("Ready")
        else:
            self.statusBar().showMessage("Still need database!")
        
    def start(self):
        self.show()
