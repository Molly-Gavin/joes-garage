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

def add_car(connection, make, model, year, location, photo_path, note, rating, date_added):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO cars (make, model, year, location, photo_path, note, rating, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (make, model, year, location, photo_path, note, rating, date_added))
    connection.commit()
    return cursor.lastrowid

if __name__ == "__main__":
    connection = create_connection()
    create_table(connection)

    new_id = add_car(
        connection,
        make="Toyota",
        model="Supra",
        year=1998,
        location="Grocery store parking lot",
        photo_path="data/photos/supra.jpg",
        note="First car I ever spotted for this",
        rating=5,
        date_added="2026-09-17"
    )

    print(f"Added car with id {new_id}")

    connection.close()
    