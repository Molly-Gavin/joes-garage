from transformers import pipeline

classifier = pipeline("image-classification", model="dima806/car_brands_image_detection")


def identify_make(photo_path):
    result = classifier(photo_path)
    top_guess = result[0]
    return top_guess["label"]
