import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    marks INTEGER,
    branch TEXT
)
""")

data = [
    ("Ravi", 85, "CSE"),
    ("Anu", 92, "ECE"),
    ("Kiran", 78, "CSE"),
    ("Sneha", 95, "IT"),
    ("Arjun", 88, "ECE")
]

cursor.executemany(
    "INSERT INTO students (name, marks, branch) VALUES (?, ?, ?)",
    data
)

conn.commit()
conn.close()

print("✅ Database created successfully!")