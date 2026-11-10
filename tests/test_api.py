import pytest
from fastapi.testclient import TestClient

import api
import database

NEW_CAR = {
    "make": "Ford",
    "model": "Mustang",
    "year": 1969,
    "location": "Car show",
    "note": "Test car",
    "rating": 5,
}


@pytest.fixture
def anonymous_client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test_garage.db"))
    monkeypatch.setattr(api, "PHOTO_DIR", str(tmp_path))
    return TestClient(api.app)


@pytest.fixture
def client(anonymous_client):
    anonymous_client.post("/login", data={"password": "test-password"})
    return anonymous_client


def test_garage_starts_empty(client):
    response = client.get("/cars")
    assert response.status_code == 200
    assert response.json() == []


def test_create_car(client):
    response = client.post("/cars", json=NEW_CAR)
    assert response.status_code == 201
    car = response.json()
    assert car["id"] == 1
    assert car["make"] == "Ford"
    assert car["date_added"] != ""


def test_rating_must_be_between_1_and_5(client):
    bad_car = dict(NEW_CAR, rating=9)
    response = client.post("/cars", json=bad_car)
    assert response.status_code == 422


def test_get_one_car(client):
    client.post("/cars", json=NEW_CAR)
    response = client.get("/cars/1")
    assert response.status_code == 200
    assert response.json()["model"] == "Mustang"


def test_get_missing_car_returns_404(client):
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
    response = client.put("/cars/1", json=changes)

    assert response.status_code == 200
    car = response.json()
    assert car["model"] == "Mustang GT"
    assert car["note"] == "Edited note"
    assert car["rating"] == 4
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
    assert client.get("/cars/1").status_code == 404


def test_delete_missing_car_returns_404(client):
    response = client.delete("/cars/999")
    assert response.status_code == 404


def test_identify_rejects_files_that_are_not_photos(client):
    response = client.post(
        "/identify",
        files={"photo": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_identify_returns_make_and_saves_photo(client):
    response = client.post(
        "/identify",
        files={"photo": ("car.jpg", b"pretend photo bytes", "image/jpeg")},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["make"] == "TestMake"
    assert result["photo_path"].endswith(".jpg")