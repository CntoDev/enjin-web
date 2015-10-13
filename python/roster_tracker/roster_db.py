import os
import shutil
import sqlite3 as lite
import sys
import time

from datetime import datetime


class RosterDatabase(object):
    def __init__(self, sqlite_dirname, strict=False):
        self._sqlite_dirname = sqlite_dirname
        self._sqlite_filename = os.path.join(sqlite_dirname, "cnto.sqlite")
        
        if not os.path.exists(self._sqlite_filename):
            if strict:
                raise ValueError("Database not found!")
            else:
                self.initialize()
        
        self.backup()
    
    def _get_connection(self):
        return lite.connect(self._sqlite_filename)
    
    def get_attendance_id(self, event_id, member_id):
        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT (id) FROM Attendance WHERE event_id = ? and member_id = ?", (event_id, member_id))
            rows = cur.fetchall()
            if len(rows) == 0:
                return None
            else:
                return rows[0][0]
    
    def get_username_id(self, username):
        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT (id) FROM Member WHERE member_name = '%s'" % (username,))
            rows = cur.fetchall()
            if len(rows) == 0:
                return None
            else:
                return rows[0][0]
    
    def get_event_id(self, event_date):
        with self._get_connection() as con:
            timestamp = time.mktime(event_date.timetuple())
            cur = con.cursor()
            cur.execute("SELECT (id) FROM Event WHERE timestamp = '%s'" % (timestamp,))
            rows = cur.fetchall()
            if len(rows) == 0:
                return None
            else:
                return rows[0][0]
    
    def get_rank_id(self, rank):
        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT (id) FROM Rank WHERE rank_name = '%s'" % (rank,))
            rows = cur.fetchall()
            if len(rows) == 0:
                return None
            else:
                return rows[0][0]
    
    def insert_rank(self, rank_name):
        """
        """
        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Rank (rank_name) VALUES('%s')" % (rank_name,))
        
            return cur.lastrowid
        
        return None
    
    def insert_member(self, username, rank_name):
        """
        """
        username_id = self.get_username_id(username) 
        if username_id is None:
            rank_id = self.get_rank_id(rank_name)
            if rank_id is None:
                rank_id = self.insert_rank(rank_name)
            
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Member (member_name, rank_id) VALUES('%s', %s)" % (username, rank_id))
                
                return cur.lastrowid
        
        return username_id
    
    def insert_event(self, event_date):
        """
        """
        event_id = self.get_event_id(event_date) 
        if event_id is None:
            timestamp = time.mktime(event_date.timetuple())
            
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Event (timestamp) VALUES(%s)" % (timestamp))
                
                return cur.lastrowid
        
        return event_id
    
    def insert_attendance(self, event_id, member_id, attendance_value):
        """
        """
        attendance_id = self.get_attendance_id(event_id, member_id)
        if attendance_id is None:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Attendance (event_id, member_id, attendance) VALUES(?, ?, ?)", (event_id, member_id, attendance_value))
                
                return cur.lastrowid
        else:
            with self._get_connection() as con:
                cur = con.cursor()
                cur.execute("UPDATE Attendance SET attendance=? WHERE id=?", (attendance_value, attendance_id))
        
        return attendance_id
    
    def insert_attendances(self, event_date, attendances):
        """
        """
        event_id = self.insert_event(event_date)
        for raw_username in attendances:
            username_parts = raw_username.split(" ")
            username = username_parts[0]
            rank = "Rec"
            if len(username_parts) > 1:
                rank = username_parts[3][0:-1]
            attendance_value = attendances[raw_username]
            
            member_id = self.insert_member(username, rank)
            
            self.insert_attendance(event_id, member_id, attendance_value)
    
    def initialize(self):
        with self._get_connection() as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE Rank(id INTEGER PRIMARY KEY, rank_name TEXT, UNIQUE(rank_name))")
            
            cur.execute("CREATE TABLE MemberGroup(id INTEGER PRIMARY KEY, group_name TEXT, UNIQUE(group_name))")
            cur.execute("INSERT INTO MemberGroup (group_name) VALUES('Alpha')")
            cur.execute("INSERT INTO MemberGroup (group_name) VALUES('Bravo')")
            cur.execute("INSERT INTO MemberGroup (group_name) VALUES('Charlie')")
            cur.execute("INSERT INTO MemberGroup (group_name) VALUES('Recruits')")
            
            cur.execute("CREATE TABLE Event(id INTEGER PRIMARY KEY, timestamp INTEGER, UNIQUE(timestamp))")
            cur.execute("CREATE TABLE Member(id INTEGER PRIMARY KEY, member_name, rank_id Integer REFERENCES Rank(id), member_group_id Integer REFERENCES MemberGroup(id), UNIQUE(member_name))")
            
            cur.execute("CREATE TABLE Attendance(id INTEGER PRIMARY KEY, event_id Integer REFERENCES Event(id), member_id Integer REFERENCES Member(id), attendance REAL, UNIQUE (event_id, member_id))")
    
    def backup(self):
        if os.path.exists(self._sqlite_filename):
            backup_filename = self._sqlite_filename + ".backup"
            if os.path.exists(backup_filename):
                os.remove(backup_filename)
                
            shutil.copy(self._sqlite_filename, backup_filename)
            
if __name__ == "__main__":
    raise Exception("NO")
    
    db = RosterDatabase("temp.sqlite")
    
    event_date = datetime(2011, 11, 11).date()
    
    overall_attendances = {u'Spartak [CNTO - Gnt]': 1.0, u'Chypsa [CNTO - Gnt]': 0.27631578947368424, u'Anders [CNTO - SPC]': 0.7236842105263158, u'Guilly': 0.7236842105263158, u'Hellfire [CNTO - SPC]': 1.0, u'Rush [CNTO - Gnt]': 0.7236842105263158, u'Hateborder [CNTO - Gnt]': 0.7236842105263158, u'Peltier [CNTO - Gnt]': 0.5394736842105263, u'John [CNTO - JrNCO]': 0.7236842105263158, u'Alos': 1.0, u'Highway [CNTO - Gnt]': 0.27631578947368424, u'Mars [CNTO - Gnt]': 0.7236842105263158, u'Skywalker [CNTO - Gnt]': 0.6052631578947368, u'Supreme [CNTO - Gnt]': 0.7236842105263158, u'Dachi [CNTO - Gnt]': 0.7236842105263158, u'Postma [CNTO - Gnt]': 0.7236842105263158, u'Obi [CNTO - JrNCO]': 0.39473684210526316, u'Chris [CNTO - SPC]': 1.0, u'Cody [CNTO - SPC]': 1.0}
    db.insert_attendances(event_date, overall_attendances)
    
    
    
