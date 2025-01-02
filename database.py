import sqlite3
import os

# Connect to SQLite database
conn = sqlite3.connect('Faces.db')
c = conn.cursor()

# Create table to store embeddings and names
c.execute('''CREATE TABLE IF NOT EXISTS faces
             (name TEXT, embedding BLOB)''')

c.execute('''CREATE TABLE IF NOT EXISTS class_routine
             (id INTEGER PRIMARY KEY,
              teacher_name TEXT,
              class_start_time TEXT,
              class_end_time TEXT,
              class_room TEXT,
              camera_index INTEGER,
              FOREIGN KEY (teacher_name) REFERENCES faces(name))''')

c.execute('''CREATE TABLE IF NOT EXISTS attendance (
             id INTEGER PRIMARY KEY,
             teacher_name TEXT,
             class_start_time TEXT,
             date TEXT,
             class_room TEXT,
             attendance_status TEXT DEFAULT 'A',
             attendance_time TEXT,
             FOREIGN KEY (teacher_name) REFERENCES faces(name));''')

# Function to drop a table
def drop_table(table_name):
    c.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()

# # Call the function to drop a table
# drop_table('attendance')

# Commit changes
conn.commit()

conn.close()