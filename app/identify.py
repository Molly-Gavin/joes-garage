# identify.py looks at a car photo and guesses the make, like Toyota or McLaren.
# It uses a pretrained model from Hugging Face, so we did not train anything ourselves.

from transformers import pipeline

# Loading the model is slow, so it happens once, when this file is first imported.
# The first run also downloads the model files. After that they are saved on your computer.
classifier = pipeline("image-classification", model="dima806/car_brands_image_detection")


def identify_make(photo_path):
    # The model returns a list of guesses, each with a label and a score from 0 to 1.
    # The list comes sorted with the most confident guess first.
    result = classifier(photo_path)
    top_guess = result[0]
    # We keep only the brand name. The model is right about 69 percent of the time,
    # which is why the web page lets you change the make before saving.
    return top_guess["label"]