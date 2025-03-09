import sys
import os
from PIL import Image
import tensorflow as tf
import numpy as np
import json  # Import json to output data as JSON

# Load the pre-trained model
model = tf.keras.models.load_model("tumor_classification_model.keras")

# Function to map prediction to class name
def names(number):
    return "It's a Tumor" if number == 0 else "No, It's not a Tumor"

def get_elaboration(diagnosis, confidence):
    """
    Provides elaboration based on the diagnosis and confidence.
    """
    if diagnosis == "It's a Tumor":
        return "The model is highly confident that this is a tumor. Immediate medical consultation is recommended."
    elif diagnosis == "No, It's not a Tumor":
        return "The model is highly confident that this is not a tumor. Regular monitoring is suggested."
    else:
        return "No elaboration available."


# Function to preprocess and predict a single image
def predict_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File not found - {image_path}")
        sys.exit(1)

    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        sys.exit(1)

    # Preprocess the image
    x = np.array(img.resize((128, 128)))  # Resize image to match model input size
    x = x.reshape(1, 128, 128, 3)  # Reshape for model input

    try:
        res = model.predict_on_batch(x)  # Make prediction
    except Exception as e:
        print(f"Error during prediction: {e}")
        sys.exit(1)

    classification = np.where(res == np.amax(res))[1][0]  # Get the predicted class
    confidence = res[0][classification] * 100  # Calculate confidence percentage

    # Prepare the result in JSON format
    diagnosis = names(classification)  # Get the diagnosis
    elaboration = get_elaboration(diagnosis, confidence)  # Get elaboration based on diagnosis and confidence

    result = {
        "diagnosis": diagnosis,
        "confidence": round(float(confidence), 2),  # Convert confidence to native Python float
        "elaboration": get_elaboration(diagnosis, confidence)
    }

    # Output the result as a JSON string
    print(json.dumps(result))  # Print JSON formatted result

# Modify script to accept dynamic input from `app.py`
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No image path provided")
        sys.exit(1)

    image_path = sys.argv[1]
    predict_image(image_path)
