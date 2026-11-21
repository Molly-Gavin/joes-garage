# api.py is the web server. It receives requests from the browser (or your phone),
# checks the login, calls the database functions, and sends answers back.

import os
import secrets
import shutil
import uuid
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel, Field
import uvicorn

from database import create_connection, create_table, get_all_cars, add_car, update_car, delete_car
from identify import identify_make

# ---------- Secrets and login settings ----------

# Read the private .env file so the password and key never appear in the code.
load_dotenv()

GARAGE_PASSWORD = os.environ.get("GARAGE_PASSWORD")
GARAGE_SECRET = os.environ.get("GARAGE_SECRET")
# Refuse to start without both secrets. A server with no password would be wide open.
if not GARAGE_PASSWORD or not GARAGE_SECRET:
    raise RuntimeError("Set GARAGE_PASSWORD and GARAGE_SECRET in the .env file")

COOKIE_NAME = "garage_login"
# A login lasts 30 days: 30 days x 24 hours x 60 minutes x 60 seconds.
SESSION_SECONDS = 30 * 24 * 60 * 60
# The signer stamps each cookie with the secret key so nobody can forge one.
signer = URLSafeTimedSerializer(GARAGE_SECRET)

# ---------- App setup ----------

app = FastAPI()

PHOTO_DIR = os.path.join("data", "photos")
ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Create the photos folder if it is missing, then share it at the /photos address
# so the web page can show saved pictures.
os.makedirs(PHOTO_DIR, exist_ok=True)
app.mount("/photos", StaticFiles(directory=PHOTO_DIR), name="photos")


# ---------- Shapes of valid data ----------
# FastAPI checks incoming data against these classes and rejects anything that does not fit.

class NewCar(BaseModel):
    make: str
    model: str
    year: int
    # A value after the equals sign makes a field optional.
    location: str = ""
    note: str = ""
    # Field(ge=1, le=5) means the rating must be at least 1 and at most 5.
    rating: int = Field(ge=1, le=5)
    photo_path: str = ""


class CarChanges(BaseModel):
    # An edit has no photo_path and no date, so an edit cannot change them.
    make: str
    model: str
    year: int
    location: str = ""
    note: str = ""
    rating: int = Field(ge=1, le=5)


# ---------- Helper functions ----------

def car_to_dict(car):
    # The database gives each car as a tuple. This labels each position
    # so the web page can read car["make"] instead of car[1].
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
    # Look through every car for the one with this id. Gives back None if there is no match.
    cars = get_all_cars(connection)
    for car in cars:
        if car[0] == car_id:
            return car
    return None


def is_logged_in(request):
    # A visitor is logged in if they carry a cookie that we signed ourselves
    # and that is less than 30 days old.
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    try:
        signer.loads(token, max_age=SESSION_SECONDS)
        return True
    except BadSignature:
        # A forged, damaged, or expired cookie ends up here.
        return False


# ---------- The lock ----------

@app.middleware("http")
async def require_login(request: Request, call_next):
    # Middleware is a guard. Every request passes through it before reaching a route.
    # The login page is open to everyone. Everything else needs a valid cookie.
    if request.url.path == "/login" or is_logged_in(request):
        return await call_next(request)
    # Someone asking for the home page without a cookie is sent to the login page.
    if request.url.path == "/":
        return RedirectResponse("/login")
    # Anything else gets 401, the web code for "not allowed".
    return JSONResponse({"detail": "Not logged in"}, status_code=401)


# ---------- Login and logout routes ----------

@app.get("/login")
def login_page():
    # Show the login page.
    return FileResponse(os.path.join("web", "login.html"))


@app.post("/login")
def login(password: str = Form(...)):
    # compare_digest compares in a way that does not leak clues through timing.
    if not secrets.compare_digest(password.encode(), GARAGE_PASSWORD.encode()):
        # 303 tells the browser to load the login page again, now showing the error.
        return RedirectResponse("/login?error=1", status_code=303)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        signer.dumps("ok"),
        max_age=SESSION_SECONDS,
        # httponly stops page scripts from reading the cookie.
        httponly=True,
        # samesite="lax" stops other websites from sending it along with their requests.
        samesite="lax",
    )
    return response


@app.post("/logout")
def logout():
    # Delete the cookie, then send the visitor back to the login page.
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------- Page and car routes ----------
# Each route pairs a web address and a request type with one function.
# GET asks for data, POST adds something, PUT changes something, DELETE removes something.

@app.get("/")
def home():
    # The main page of the app.
    return FileResponse(os.path.join("web", "index.html"))


@app.get("/cars")
def list_cars():
    # Send back every car, with labeled fields.
    connection = create_connection()
    cars = get_all_cars(connection)
    connection.close()
    return [car_to_dict(car) for car in cars]


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    # The {car_id} in the address is read as a whole number.
    connection = create_connection()
    car = find_car(connection, car_id)
    connection.close()

    if car is None:
        # 404 is the web code for "not found".
        raise HTTPException(status_code=404, detail="Car not found")

    return car_to_dict(car)


@app.post("/identify")
def identify_photo(photo: UploadFile = File(...)):
    # Receive a photo, save it, and ask the model to guess the make.
    extension = os.path.splitext(photo.filename)[1].lower()
    # Never trust what a browser sends. Only accept real photo file types.
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Please upload a JPG or PNG photo")

    # A random name keeps two uploads called IMG_1.jpg from overwriting each other.
    saved_name = f"{uuid.uuid4().hex}{extension}"
    saved_path = os.path.join(PHOTO_DIR, saved_name)

    # Copy the uploaded file onto the disk.
    with open(saved_path, "wb") as saved_file:
        shutil.copyfileobj(photo.file, saved_file)

    make = identify_make(saved_path)
    return {"make": make, "photo_path": saved_path}


@app.post("/cars", status_code=201)
def create_car(new_car: NewCar):
    # 201 is the web code for "created". FastAPI already checked new_car against NewCar.
    connection = create_connection()
    new_id = add_car(
        connection,
        make=new_car.make,
        model=new_car.model,
        year=new_car.year,
        location=new_car.location,
        photo_path=new_car.photo_path,
        note=new_car.note,
        rating=new_car.rating,
        # The server sets the date, so the browser cannot choose it.
        date_added=str(date.today()),
    )
    car = find_car(connection, new_id)
    connection.close()
    return car_to_dict(car)


@app.put("/cars/{car_id}")
def change_car(car_id: int, changes: CarChanges):
    # Change an existing car. The photo and the date added stay as they were.
    connection = create_connection()
    existing_car = find_car(connection, car_id)

    if existing_car is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Car not found")

    update_car(
        connection,
        car_id=car_id,
        make=changes.make,
        model=changes.model,
        year=changes.year,
        location=changes.location,
        # Positions 5 and 8 in the tuple are photo_path and date_added.
        photo_path=existing_car[5],
        note=changes.note,
        rating=changes.rating,
        date_added=existing_car[8],
    )
    updated_car = find_car(connection, car_id)
    connection.close()
    return car_to_dict(updated_car)


@app.delete("/cars/{car_id}")
def remove_car(car_id: int):
    # Look the car up first, so a missing id gets a clear 404 instead of silently doing nothing.
    connection = create_connection()
    car = find_car(connection, car_id)

    if car is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Car not found")

    delete_car(connection, car_id)
    connection.close()
    return {"message": f"Deleted car {car_id}"}


# This block runs only when you start the file directly with: python3 app/api.py
# The host 0.0.0.0 lets other devices on your home wifi, like your phone, reach the server.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)