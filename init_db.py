import sqlite3

# Initialize the database
db = sqlite3.connect("example.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
""")
cursor = db.cursor()
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO users (name, age) VALUES (?, ?)",
        [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
    )
db.commit()
db.close()
print("Database initialized.")