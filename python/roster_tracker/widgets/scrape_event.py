import sys
from datetime import datetime
from PySide import QtGui, QtCore


class ScrapeEventWidget(QtGui.QWidget):
    def __init__(self, viewer):
        super(ScrapeEventWidget, self).__init__()
        self._selected_scrape_date = None
        
        self._viewer = viewer
        
        self._layout = QtGui.QGridLayout()
        
        self._calendar = QtGui.QCalendarWidget(self)
        self._calendar.setGridVisible(True)
        self._layout.addWidget(self._calendar, 0, 0)
        
        start_row = QtGui.QWidget(self)
        start_row_layout = QtGui.QGridLayout()
        start_row_layout.addWidget(QtGui.QLabel("Start hour"), 0, 0)
        self._start_time_edit = QtGui.QLineEdit("18")
        self._start_time_edit.setMaximumHeight(25)
        start_row_layout.addWidget(self._start_time_edit, 0, 1)
        start_row.setLayout(start_row_layout)
        start_row.setMaximumHeight(50)
        self._layout.addWidget(start_row, 1, 0)
        
        end_row = QtGui.QWidget(self)
        end_row_layout = QtGui.QGridLayout()
        end_row_layout.addWidget(QtGui.QLabel("End hour"), 0, 0)
        self._end_time_edit = QtGui.QLineEdit("20")
        self._end_time_edit.setMaximumHeight(25)
        end_row_layout.addWidget(self._end_time_edit, 0, 1)
        end_row.setLayout(end_row_layout)
        end_row.setMaximumHeight(50)
        self._layout.addWidget(end_row, 2, 0)

        self._scrape_button = QtGui.QPushButton("Scrape!")
        self._scrape_button.clicked.connect(self.scrape_pushed)
        self._layout.addWidget(self._scrape_button, 3, 0)
        
        self.setLayout(self._layout)
        
    def scrape_pushed(self):

        success = False 
        try:
            qt_date = self._calendar.selectedDate()
            dt = datetime(qt_date.year(), qt_date.month(), qt_date.day())
            
            start_hour = int(self._start_time_edit.text())
            assert 0 <= start_hour < 24
            end_hour = int(self._end_time_edit.text())
            assert 0 <= end_hour < 24
            success = True
        except Exception:
            self._viewer.show_message("Error", "Invalid input for scraping!")
        
        if success:
            self._viewer.scrape(dt, start_hour, end_hour)
