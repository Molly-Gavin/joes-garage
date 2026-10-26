import os
import shutil
import uuid
from datetime import date

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from database import create_connection, create_table, get_all_cars, add_car, delete_car
from identify import identify_make

app = FastAPI()

PHOTO_DIR = os.path.join("data", "photos")
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png")

os.makedirs(PHOTO_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=PHOTO_DIR), name="photos")


class NewCar(BaseModel):
    make: str
    model: str
    year: int
    location: str = ""
    note: str = ""
    rating: int = Field(ge=1, le=5)
    photo_path: str = ""


def car_to_dict(car):
    return {
        "id": car[0],
        "make": car[1],
        "model": car[2],
        "year": car[3],
        "location": car[4],
        "photo_path": car[5],
        "note": car[6],
        "rating": car[7],
        "date_added": car[8],
    }


def find_car(connection, car_id):
    cars = get_all_cars(connection)
    for car in cars:
        if car[0] == car_id:
            return car
    return None


@app.get("/")
def home():
    return FileResponse(os.path.join("web", "index.html"))


@app.get("/cars")
def list_cars():
    connection = create_connection()
    create_table(connection)
    cars = get_all_cars(connection)
    connection.close()
    return [car_to_dict(car) for car in cars]


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    connection = create_connection()
    car = find_car(connection, car_id)
    connection.close()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    return car_to_dict(car)


@app.post("/identify")
def identify_photo(photo: UploadFile = File(...)):
    extension = os.path.splitext(photo.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Please upload a JPG or PNG photo")

    saved_name = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(PHOTO_DIR, saved_name)

    with open(saved_path, "wb") as saved_file:
        shutil.copyfileobj(photo.file, saved_file)

    make = identify_make(saved_path)
    return {"make": make, "photo_path": saved_path}


@app.post("/cars", status_code=201)
def create_car(new_car: NewCar):
    connection = create_connection()
    create_table(connection)
    new_id = add_car(
        connection,
        make=new_car.make,
        model=new_car.model,
        year=new_car.year,
        location=new_car.location,
        photo_path=new_car.photo_path,
        note=new_car.note,
        rating=new_car.rating,
        date_added=str(date.today()),
    )
    car = find_car(connection, new_id)
    connection.close()
    return car_to_dict(car)


@app.delete("/cars/{car_id}")
def remove_car(car_id: int):
    connection = create_connection()
    car = find_car(connection, car_id)

    if car is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Car not found")

    delete_car(connection, car_id)
    connection.close()
    return {"message": f"Deleted car {car_id}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)