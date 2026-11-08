import sqlite3

from database import create_table, add_car, get_all_cars, update_car, delete_car


def make_test_connection():
    connection = sqlite3.connect(":memory:")
    create_table(connection)
    return connection


def add_sample_car(connection, make="Toyota", rating=5):
    return add_car(
        connection,
        make=make,
        model="Supra",
        year=1998,
        location="Parking lot",
        photo_path="",
        note="Test car",
        rating=rating,
        date_added="2026-01-01",
    )


def test_add_car_returns_an_id():
    connection = make_test_connection()
    new_id = add_sample_car(connection)
    assert new_id == 1


def test_get_all_cars_returns_every_car():
    connection = make_test_connection()
    add_sample_car(connection, make="Toyota")
    add_sample_car(connection, make="Honda")

    cars = get_all_cars(connection)

    assert len(cars) == 2
    assert cars[0][1] == "Toyota"
    assert cars[1][1] == "Honda"


def test_update_car_changes_values_and_keeps_date():
    connection = make_test_connection()
    car_id = add_sample_car(connection)

    update_car(
        connection,
        car_id=car_id,
        make="Ford",
        model="Mustang",
        year=1969,
        location="Car show",
        photo_path="",
        note="Edited",
        rating=3,
        date_added="2026-01-01",
    )

    car = get_all_cars(connection)[0]
    assert car[1] == "Ford"
    assert car[2] == "Mustang"
    assert car[7] == 3
    assert car[8] == "2026-01-01"


def test_delete_car_removes_only_that_car():
    connection = make_test_connection()
    first_id = add_sample_car(connection, make="Toyota")
    add_sample_car(connection, make="Honda")

    delete_car(connection, first_id)

    cars = get_all_cars(connection)
    assert len(cars) == 1
    assert cars[0][1] == "Honda"