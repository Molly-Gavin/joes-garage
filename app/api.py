from fastapi import FastAPI
import uvicorn

from database import create_connection, create_table, get_all_cars

app = FastAPI()


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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)