import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import os
import sys
import json

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

# Load model
model_path = r"C:\Users\Mallikarjun\OneDrive\Desktop\Project_i\btmodel.keras"
model = tf.keras.models.load_model(model_path)

def get_elaboration(diagnosis):
    """Generate explanation based on diagnosis."""
    elaborations = {
        "No tumor": "The model is highly confident that this is not a tumor. Regular monitoring is suggested.",
        "Glioma Tumor": "The model is highly confident that this is a Glioma Tumor. Immediate medical consultation is recommended.",
        "Meningioma Tumor": "The model is highly confident that this is a Meningioma Tumor. Immediate medical consultation is recommended.",
        "Pituitary Tumor": "The model is highly confident that this is a Pituitary Tumor. Immediate medical consultation is recommended."
    }
    return elaborations.get(diagnosis, "No elaboration available.")

def predict_image(image_path):
    """Process image and return prediction results."""
    try:
        # Load and preprocess image
        img = Image.open(image_path)
        opencvImage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.resize(opencvImage, (150, 150))
        img = img.reshape(1, 150, 150, 3)
        
        # Predict class probabilities
        p = model.predict(img, verbose=0)
        
        # Get predicted class and confidence
        class_idx = np.argmax(p, axis=1)[0]
        confidence = float(np.max(p)) * 100  # Convert to percentage

        # Map class index to tumor type
        tumor_types = {
            0: "Glioma Tumor",
            1: "No tumor",
            2: "Meningioma Tumor",
            3: "Pituitary Tumor"
        }
        diagnosis = tumor_types.get(class_idx, "Unknown")

        return diagnosis, confidence

    except Exception as e:
        print(f'Error processing image: {e}', file=sys.stderr)
        return None, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}), file=sys.stderr)
        sys.exit(1)

    # Get prediction
    diagnosis, confidence = predict_image(sys.argv[1])
    
    if diagnosis is None:
        print(json.dumps({"error": "Failed to process image"}), file=sys.stderr)
        sys.exit(1)

    # Prepare and print result
    result = {
        "diagnosis": diagnosis,
        "confidence": f"{confidence:.2f}%",
        "elaboration": get_elaboration(diagnosis)
    }
    print(json.dumps(result))