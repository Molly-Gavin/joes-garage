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

def get_all_cars(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()
    return rows

