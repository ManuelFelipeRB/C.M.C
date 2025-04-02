import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='weights.db'):
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weight_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    time TEXT,
                    plate TEXT,
                    axes TEXT,
                    initial_weight FLOAT,
                    final_weight FLOAT,
                    tare TEXT,
                    net_weight FLOAT
                )
            ''')
            conn.commit()

    def add_weight_event(self, date, time, plate, axes, initial_weight, final_weight, tare, net_weight):
        """Add a new weight event to the database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weight_events 
                (date, time, plate, axes, initial_weight, final_weight, tare, net_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, time, plate, axes, initial_weight, final_weight, tare, net_weight))
            conn.commit()
            return cursor.rowcount

    def get_weight_events(self):
        """Retrieve all weight events"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM weight_events ORDER BY id DESC')
            return cursor.fetchall()