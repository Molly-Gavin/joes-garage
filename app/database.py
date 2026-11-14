# database.py holds every function that talks to the SQLite database.
# The rest of the app calls these functions and never writes SQL itself.

import sqlite3
import os

# Where the database file lives, built so it works on Mac and Windows.
DB_PATH = os.path.join("data", "garage.db")


def create_connection():
    # Open the database file. SQLite creates the file if it does not exist yet.
    connection = sqlite3.connect(DB_PATH)
    # Make sure the cars table exists every time we open the database.
    # This also protects a brand new copy of the project from errors.
    create_table(connection)
    return connection


def create_table(connection):
    # A cursor is the tool that sends SQL commands to the database.
    cursor = connection.cursor()
    # IF NOT EXISTS means running this twice does no harm.
    # The id column is a number the database fills in by itself, one higher each time.
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
    # commit saves the change to the file for good.
    connection.commit()


def add_car(connection, make, model, year, location, photo_path, note, rating, date_added):
    cursor = connection.cursor()
    # The question marks are placeholders. SQLite fills them in from the tuple below,
    # in order. This keeps typed text from being treated as SQL commands,
    # which blocks a kind of attack called SQL injection.
    cursor.execute("""
        INSERT INTO cars (make, model, year, location, photo_path, note, rating, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (make, model, year, location, photo_path, note, rating, date_added))
    connection.commit()
    # Give back the id the database just assigned to the new car.
    return cursor.lastrowid


def update_car(connection, car_id, make, model, year, location, photo_path, note, rating, date_added):
    cursor = connection.cursor()
    # WHERE id = ? limits the change to one car. Without it, every car would change.
    cursor.execute("""
        UPDATE cars
        SET make = ?, model = ?, year = ?, location = ?, photo_path = ?, note = ?, rating = ?, date_added = ?
        WHERE id = ?
    """, (make, model, year, location, photo_path, note, rating, date_added, car_id))
    connection.commit()


def delete_car(connection, car_id):
    cursor = connection.cursor()
    # A one value tuple needs the comma after car_id, or Python reads it as plain parentheses.
    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    connection.commit()


def get_all_cars(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars")
    # Each car comes back as a tuple in column order:
    # id, make, model, year, location, photo_path, note, rating, date_added.
    return cursor.fetchall()


def get_cars_by_date(connection):
    cursor = connection.cursor()
    # DESC means largest first, so the newest dates come first.
    cursor.execute("SELECT * FROM cars ORDER BY date_added DESC")
    return cursor.fetchall()


def get_cars_by_rating(connection):
    cursor = connection.cursor()
    # Highest rated cars come first, so favorites rise to the top.
    cursor.execute("SELECT * FROM cars ORDER BY rating DESC")
    return cursor.fetchall()


def get_cars_by_location(connection, location):
    cursor = connection.cursor()
    # LIKE matches loosely. The percent signs mean any text can come before or after,
    # so typing "grocery" finds "Grocery store parking lot".
    cursor.execute("SELECT * FROM cars WHERE location LIKE ?", (f"%{location}%",))
    return cursor.fetchall()