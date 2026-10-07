from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from database import create_connection, create_table, get_all_cars, add_car, delete_car

app = FastAPI()


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
    return {"message": "Welcome to Joe's Garage"}


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
    uvicorn.run(app, host="127.0.0.1", port=8000)