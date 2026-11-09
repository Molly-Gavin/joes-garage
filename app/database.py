import sqlite3
import os
from datetime import date

DB_PATH = os.path.join("data", "garage.db")


def create_connection():
    connection = sqlite3.connect(DB_PATH)
    create_table(connection)
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

def update_car(connection, car_id, make, model, year, location, photo_path, note, rating, date_added):
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE cars
        SET make = ?, model = ?, year = ?, location = ?, photo_path = ?, note = ?, rating = ?, date_added = ?
        WHERE id = ?
    """, (make, model, year, location, photo_path, note, rating, date_added, car_id))
    connection.commit()

def delete_car(connection, car_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    connection.commit()

def get_all_cars(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars")
    rows = cursor.fetchall()
    return rows

def get_cars_by_date(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY date_added DESC")
    return cursor.fetchall()


def get_cars_by_rating(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY rating DESC")
    return cursor.fetchall()


def get_cars_by_location(connection, location):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars WHERE location LIKE ?", (f"%{location}%",))
    return cursor.fetchall()

