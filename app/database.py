import sqlite3
import os

DB_PATH = os.path.join("data", "garage.db")


def create_connection():
    connection = sqlite3.connect(DB_PATH)
    return connection


def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            location TEXT,
            photo_path TEXT,
            note TEXT,
            rating INTEGER,
            date_added TEXT
        )
    """)
    connection.commit()


if __name__ == "__main__":
    connection = create_connection()
    create_table(connection)
    connection.close()
    print("Database and table created successfully.")