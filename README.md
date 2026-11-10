# Joe's Garage
![Tests](https://github.com/Molly-Gavin/joes-garage/actions/workflows/tests.yml/badge.svg)

A web app for spotting cars. Take a photo of a car, and the app guesses the make. Then add the model, year, where you saw it, a note, and a rating from 1 to 5. Every car is saved in your own garage.

## What it does

- Detects the car make from a photo using a pretrained image model
- Saves cars in a local SQLite database
- Shows the garage as cards with photos
- Lets you add, edit, and delete cars
- Works on a phone browser over home wifi

## Built with

- Python
- FastAPI and uvicorn for the API
- SQLite for storage
- Hugging Face transformers with the dima806/car_brands_image_detection model
- Plain HTML and JavaScript for the web page
- pytest for tests

## How to run it

1. Clone the project and open a terminal in its folder.
2. Create and turn on a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

3. Install what it needs:

```
pip install fastapi uvicorn python-multipart transformers torch pillow pytest
```

4. Start the server:

```
python3 app/api.py
```

5. Open http://127.0.0.1:8000 in a browser.

The first start downloads the photo model, about 340 MB. After that it starts faster.

To use it on a phone, connect the phone to the same wifi as your computer and open `http://YOUR_COMPUTER_ADDRESS:8000`.

## Run the tests

```
python3 -m pytest
```

## Things to know

- The model only guesses the make, and it is right about 69 percent of the time. You can change the make before saving.
- There is no login. Run it on a home network only, and stop the server when you are done.
- Photos and the database stay on your computer and are not uploaded to GitHub.

## Project layout

- `app/api.py` holds the web routes
- `app/database.py` holds the database functions
- `app/identify.py` runs the photo model
- - `app/main.py` is an optional command line version of the app. Run it with `python3 app/main.py`
- `web/index.html` is the web page
- `tests/` holds the automated tests