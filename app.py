from flask import Flask, request, render_template, jsonify, send_file
import os
import subprocess
import uuid  # To generate unique filenames
import json  # To handle JSON responses
import io  # For handling in-memory files
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Limit file size to 5MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/upload-brain")
def upload_brain():
    return render_template("upload_brain.html")

@app.route("/upload-pneumonia")
def upload_pneumonia():
    return render_template("upload_pneumonia.html")

@app.route("/predict-brain", methods=["POST"])
def predict_brain():
    """Handle brain tumor image upload and send it to test.py."""
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload a PNG, JPG, or JPEG image."}), 400

    # Generate a unique filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)

    abs_file_path = os.path.abspath(file_path)

    # Call test.py and capture the JSON output
    try:
        result = subprocess.run(
            ["python", "test.py", abs_file_path], 
            capture_output=True, text=True, check=True
        )
        
        # Parse the JSON output from test.py
        prediction = json.loads(result.stdout.strip())  # Parse the JSON result

        # Extract the necessary details
        diagnosis = prediction.get("diagnosis", "Unknown")
        confidence = prediction.get("confidence", "N/A")
        elaboration = prediction.get("elaboration", "No elaboration available.")

        # Pass the results to the template
        return render_template("result.html", image_path=f"uploads/{unique_filename}", diagnosis=diagnosis, confidence=confidence, elaboration=elaboration)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else str(e)
        return render_template("result.html", image_path=f"uploads/{unique_filename}", diagnosis="Error", confidence="N/A", elaboration=f"Error: {error_message}")

@app.route("/predict-pneumonia", methods=["POST"])
def predict_pneumonia():
    """Handle pneumonia image upload and send it to test2.py."""
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload a PNG, JPG, or JPEG image."}), 400

    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(file_path)

    abs_file_path = os.path.abspath(file_path)

    try:
        result = subprocess.run(
            ["python", "test2.py", abs_file_path],  # Make sure test2.py is used for pneumonia
            capture_output=True, text=True, check=True
        )
        
        prediction = json.loads(result.stdout.strip())  # Parse the JSON result

        # Extract the necessary details
        diagnosis = prediction.get("diagnosis", "Unknown")
        confidence = prediction.get("confidence", "N/A")
        elaboration = prediction.get("elaboration", "No elaboration available.")

        # Pass the results to the template
        return render_template("result.html", image_path=f"uploads/{unique_filename}", diagnosis=diagnosis, confidence=confidence, elaboration=elaboration)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else str(e)
        return render_template("result.html", image_path=f"uploads/{unique_filename}", diagnosis="Error", confidence="N/A", elaboration=f"Error: {error_message}")

@app.route("/download_report")
def download_report():
    """Generate and download the PDF report."""
    # Example data; replace this with actual dynamic data passed to the template
    diagnosis = "Tumor Detected"
    confidence = 95
    elaboration = "The model detected a high probability of a brain tumor."

    # Create a byte stream to hold the PDF data
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Add content to the PDF
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Diagnosis Report")
    c.drawString(100, 730, f"Diagnosis: {diagnosis}")
    c.drawString(100, 710, f"Confidence: {confidence}%")
    c.drawString(100, 690, f"Elaboration: {elaboration}")
    
    # Save the PDF
    c.save()

    # Move buffer's cursor to the beginning and return the PDF as a response
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="diagnosis_report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
