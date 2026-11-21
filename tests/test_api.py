# These tests check the web routes in api.py, the way a browser would use them.
# Each test starts with a brand new empty database, so tests cannot disturb each other
# or your real garage.

import pytest
from fastapi.testclient import TestClient

import api
import database

# A sample car that many tests send to the server.
NEW_CAR = {
    "make": "Ford",
    "model": "Mustang",
    "year": 1969,
    "location": "Car show",
    "note": "Test car",
    "rating": 5,
}


# A fixture is a setup function. A test that lists it as an input receives what it returns.

@pytest.fixture
def anonymous_client(tmp_path, monkeypatch):
    # tmp_path is a temporary folder that pytest creates and deletes for us.
    # monkeypatch swaps the real database and photo folder for temporary ones,
    # only while this test runs.
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test_garage.db"))
    monkeypatch.setattr(api, "PHOTO_DIR", str(tmp_path))
    # TestClient acts like a browser, but talks to the app directly with no real server.
    return TestClient(api.app)


@pytest.fixture
def client(anonymous_client):
    # The same stand in browser, but already logged in with the test password.
    # It keeps the login cookie, so later requests are allowed through the lock.
    anonymous_client.post("/login", data={"password": "test-password"})
    return anonymous_client


# ---------- Tests for the car routes ----------

def test_garage_starts_empty(client):
    response = client.get("/cars")
    assert response.status_code == 200
    assert response.json() == []


def test_create_car(client):
    response = client.post("/cars", json=NEW_CAR)
    # 201 means "created".
    assert response.status_code == 201
    car = response.json()
    assert car["id"] == 1
    assert car["make"] == "Ford"
    # The server filled in the date, so it must not be empty.
    assert car["date_added"] != ""


def test_rating_must_be_between_1_and_5(client):
    # dict(NEW_CAR, rating=9) copies the sample car and changes only the rating.
    bad_car = dict(NEW_CAR, rating=9)
    response = client.post("/cars", json=bad_car)
    # 422 is the code FastAPI uses for data that fails its checks.
    assert response.status_code == 422


def test_get_one_car(client):
    client.post("/cars", json=NEW_CAR)
    response = client.get("/cars/1")
    assert response.status_code == 200
    assert response.json()["model"] == "Mustang"


def test_get_missing_car_returns_404(client):
    # 404 means "not found".
    response = client.get("/cars/999")
    assert response.status_code == 404


def test_edit_changes_values_but_keeps_photo_and_date(client):
    original = client.post(
        "/cars", json=dict(NEW_CAR, photo_path="data/photos/abc.jpg")
    ).json()

    changes = {
        "make": "Ford",
        "model": "Mustang GT",
        "year": 1969,
        "location": "Car show",
        "note": "Edited note",
        "rating": 4,
    }
    # PUT is the request type for changing something that already exists.
    response = client.put("/cars/1", json=changes)

    assert response.status_code == 200
    car = response.json()
    assert car["model"] == "Mustang GT"
    assert car["note"] == "Edited note"
    assert car["rating"] == 4
    # An edit must not touch the photo or the date the car was added.
    assert car["photo_path"] == "data/photos/abc.jpg"
    assert car["date_added"] == original["date_added"]


def test_edit_missing_car_returns_404(client):
    changes = {
        "make": "Ford",
        "model": "Mustang",
        "year": 1969,
        "rating": 4,
    }
    response = client.put("/cars/999", json=changes)
    assert response.status_code == 404


def test_delete_car(client):
    client.post("/cars", json=NEW_CAR)
    response = client.delete("/cars/1")
    assert response.status_code == 200
    # After the delete, asking for the same car must give 404.
    assert client.get("/cars/1").status_code == 404


def test_delete_missing_car_returns_404(client):
    response = client.delete("/cars/999")
    assert response.status_code == 404


# ---------- Tests for photo upload ----------

def test_identify_rejects_files_that_are_not_photos(client):
    # 400 means the request itself was wrong. Here the file is a text file, not a photo.
    response = client.post(
        "/identify",
        files={"photo": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_identify_returns_make_and_saves_photo(client):
    # The bytes only pretend to be a photo. The stand in model never looks at them.
    response = client.post(
        "/identify",
        files={"photo": ("car.jpg", b"pretend photo bytes", "image/jpeg")},
    )
    assert response.status_code == 200
    result = response.json()
    # "TestMake" is the answer from the stand in set up in conftest.py.
    assert result["make"] == "TestMake"
    assert result["photo_path"].endswith(".jpg")


# ---------- Tests for the login lock ----------

def test_cars_are_locked_without_login(anonymous_client):
    # 401 means "not allowed", because there is no login cookie.
    response = anonymous_client.get("/cars")
    assert response.status_code == 401


def test_home_page_redirects_to_login(anonymous_client):
    # follow_redirects=False lets the test see the redirect itself.
    response = anonymous_client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/login"


def test_wrong_password_is_rejected(anonymous_client):
    response = anonymous_client.post(
        "/login", data={"password": "wrong"}, follow_redirects=False
    )
    # A wrong password sends the visitor back to the login page with an error flag.
    assert response.headers["location"] == "/login?error=1"
    # And the garage stays locked.
    assert anonymous_client.get("/cars").status_code == 401


def test_correct_password_unlocks_the_garage(anonymous_client):
    anonymous_client.post("/login", data={"password": "test-password"})
    assert anonymous_client.get("/cars").status_code == 200


def test_forged_cookie_is_rejected(anonymous_client):
    # A made up cookie was not signed with the secret key, so the lock must refuse it.
    anonymous_client.cookies.set("garage_login", "not-a-real-cookie")
    assert anonymous_client.get("/cars").status_code == 401


def test_logout_locks_the_garage_again(client):
    assert client.get("/cars").status_code == 200
    client.post("/logout")
    assert client.get("/cars").status_code == 401