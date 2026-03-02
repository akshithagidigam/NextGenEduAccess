import sqlite3

conn = sqlite3.connect("nextgenedu.db")
cur = conn.cursor()

# DROP old attendance table
cur.execute("DROP TABLE IF EXISTS attendance")

# CREATE correct attendance table
cur.execute("""
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    period1 TEXT,
    period2 TEXT,
    period3 TEXT,
    period4 TEXT,
    period5 TEXT,
    period6 TEXT
)
""")

conn.commit()
conn.close()

print("✅ Attendance table reset successfully")
