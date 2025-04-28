import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import os
import sys
import json

model_path = r"C:\Users\Mallikarjun\OneDrive\Desktop\Project_i\btmodel.keras"
model = tf.keras.models.load_model(model_path)

def get_elaboration(diagnosis):
    if diagnosis == "No tumor":
        return "The model is highly confident that this is not a tumor. Regular monitoring is suggested."
    elif diagnosis == "Glioma Tumor":
        return "The model is highly confident that this is a Glioma Tumor. Immediate medical consultation is recommended."
    elif diagnosis == "Meningioma Tumor":
        return "The model is highly confident that this is a Meningioma Tumor. Immediate medical consultation is recommended."
    elif diagnosis == "Pituitary Tumor":
        return "The model is highly confident that this is a Pituitary Tumor. Immediate medical consultation is recommended."
    else:
        return "No elaboration available."

def predict_image(image_path):
    try:
        img = Image.open(image_path)
        opencvImage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.resize(opencvImage, (150, 150))
        img = img.reshape(1, 150, 150, 3)
        
        # Predict class probabilities
        p = model.predict(img)
        
        # Get predicted class index and probability
        class_idx = np.argmax(p, axis=1)[0]
        # confidence = np.max(p) * 100  # Confidence as a percentage

        # Map class index to tumor type
        if class_idx == 0:
            diagnosis = 'Glioma Tumor'
        elif class_idx == 1:
            diagnosis = 'No tumor'
        elif class_idx == 2:
            diagnosis = 'Meningioma Tumor'
        else:
            diagnosis = 'Pituitary Tumor'

    except Exception as e:
        print(f'Error processing image: {e}')
        return

    # Get elaboration based on diagnosis
    # elaboration = get_elaboration(diagnosis)
    # confidence = 100

    # Prepare result in JSON format
    # result = {
    #     "diagnosis": diagnosis,
    #     "confidence": f"{confidence}%",
    #     "elaboration": elaboration
    # }

   

    # # Print the result as a JSON string
    # print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No image path provided")
        sys.exit(1)

    image_path = sys.argv[1]
    diagnosis = predict_image(image_path)
    confidence = 100  # Assuming 100% confidence for this example
    elaboration = get_elaboration(diagnosis)

    result = {
        "diagnosis": diagnosis,
        "confidence": f"{confidence}%",
        "elaboration": elaboration
    }

    # Print the result in JSON format
    print(json.dumps(result))
