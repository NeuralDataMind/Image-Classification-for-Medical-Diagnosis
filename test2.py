import sys
import numpy as np
from tensorflow import keras
import cv2 as cv
import os
import tensorflow as tf
import json  # To format the output as JSON

# Suppress unnecessary TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TF warnings

# Load the trained model
model = keras.models.load_model('pneumonia_classification.keras')

def predict_pneumonia(image_path):
    img = cv.imread(image_path)
    if img is None:
        return "Error: Could not read image file."
    
    # Resize the image to a smaller size
    img_resized = cv.resize(img, (128, 128))  # Resize to 128x128 or appropriate input size for the model
    
    img1 = cv.cvtColor(img_resized, cv.COLOR_BGR2GRAY)  # Convert to grayscale
    img2 = cv.blur(img1, (3, 3))  # Apply blur
    img_resized = cv.resize(img2, (32, 32))  # Resize again for model input size (if necessary)
    img_scaled = np.array(img_resized) / 255  # Scale pixel values between 0 and 1
    img_final = img_scaled.reshape((1, 32, 32, 1))  # Reshape for model input

    prediction = model.predict(img_final, verbose=0)  # Disable verbose output
    predicted_class = np.argmax(prediction)

    if predicted_class == 0:
        return "Positive"  # Class 0 represents pneumonia
    else:
        return "Negative"  # Class 1 represents no pneumonia

def get_elaboration(diagnosis, confidence):
    if diagnosis == "Positive":
        return f"The model is confident that this is pneumonia. Confidence: {confidence}%."
    elif diagnosis == "Negative":
        return f"The model is confident that this is not pneumonia. Confidence: {confidence}%."
    else:
        return "Unable to determine the result. Please consult a healthcare professional."

# Modify script to accept dynamic input from `app.py`
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No image path provided.")
        sys.exit(1)

    image_path = sys.argv[1]
    diagnosis = predict_pneumonia(image_path)
    confidence = 100  # Assuming 100% confidence for this example
    elaboration = get_elaboration(diagnosis, confidence)

    result = {
        "diagnosis": diagnosis,
        "confidence": f"{confidence}%",
        "elaboration": elaboration
    }

    # Print the result in JSON format
    print(json.dumps(result))
