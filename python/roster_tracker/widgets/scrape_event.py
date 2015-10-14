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
        self._scrape_button.clicked.connect(self.scrape_pressed)
        self._layout.addWidget(self._scrape_button, 3, 0)
        
        self._clear_button = QtGui.QPushButton("Clear attendance for date...")
        self._clear_button.clicked.connect(self.clear_date_pressed)
        self._layout.addWidget(self._clear_button, 4, 0)
        
        self.setLayout(self._layout)
        
        self.format_calendar()
    
    def refresh(self):
        self.format_calendar()
    
    def clear_date_format(self, dt):
        clear_day_format = QtGui.QTextCharFormat();
        
        qdt = QtCore.QDate(dt.year, dt.month, dt.day);
        self._calendar.setDateTextFormat(qdt, clear_day_format);
    
    def format_calendar(self):
        dts = self._viewer._control.get_all_event_dates()
        for dt in dts:
            scraped_day_format = QtGui.QTextCharFormat();
            scraped_day_format.setBackground(QtGui.QBrush(QtGui.QColor(100, 200, 100)));
    
            qdt = QtCore.QDate(dt.year, dt.month, dt.day);
            self._calendar.setDateTextFormat(qdt, scraped_day_format);
    
    def clear_date_pressed(self):
        
        qt_date = self._calendar.selectedDate()
        dt = datetime(qt_date.year(), qt_date.month(), qt_date.day())
        should_clear = self._viewer.ask_yes_no_question("Question", 
                                                        "Clear all attendance information for %s?" % (dt.strftime("%Y-%m-%d"), ))
        
        if should_clear:
            self._viewer._control.clear_attendance_for_date(dt)
            self.clear_date_format(dt)
            self.format_calendar()
    
    def scrape_pressed(self):

        success = False 
        try:
            qt_date = self._calendar.selectedDate()
            dt = datetime(qt_date.year(), qt_date.month(), qt_date.day())
            
            if dt.weekday() not in [0, 2, 4]:
                if not self._viewer.ask_yes_no_question("Question", "Date is not Monday, Wednesday or Friday.  Proceed?"):
                    return
            
            start_hour = int(self._start_time_edit.text())
            assert 0 <= start_hour < 24
            end_hour = int(self._end_time_edit.text())
            assert 0 <= end_hour < 24
            success = True
        except Exception, e:
            self._viewer.show_message("Error", "Invalid input for scraping!\n%s" % (e, ))
        
        if success:
            self._viewer.scrape(dt, start_hour, end_hour)
