import sys
from PySide import QtGui, QtCore


class ExportDataWidget(QtGui.QWidget):
    def __init__(self, viewer):
        super(ExportDataWidget, self).__init__()
        self._viewer = viewer

        self._layout = QtGui.QGridLayout()
        
        self._start_calendar = QtGui.QCalendarWidget(self)
        self._start_calendar.setGridVisible(True)
        self._layout.addWidget(self._start_calendar, 0, 0)
        self._end_calendar = QtGui.QCalendarWidget(self)
        self._end_calendar.setGridVisible(True)
        self._layout.addWidget(self._end_calendar, 0, 1)
        
        self.setLayout(self._layout)