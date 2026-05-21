import sqlite3

conn = sqlite3.connect("family_memory.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_input TEXT
)
""")

conn.commit()


def save_memory(text):
    cursor.execute(
        "INSERT INTO memories (user_input) VALUES (?)",
        (text,)
    )

    conn.commit()


def get_memories():

    cursor.execute(
        "SELECT user_input FROM memories"
    )

    rows = cursor.fetchall()

    return [row[0] for row in rows]