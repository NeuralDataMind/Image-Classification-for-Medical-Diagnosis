from flask import Flask, request, render_template, jsonify, send_file
import os
import subprocess
import uuid
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_prediction(script_name, file):
    """Generic prediction handler for both brain tumor and pneumonia."""
    if not file or not allowed_file(file.filename):
        return None, "Invalid file type. Use PNG, JPG, or JPEG.", 400

    try:
        # Save file with UUID
        unique_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        # Run prediction script
        result = subprocess.run(
            ["python", f"{script_name}.py", os.path.abspath(file_path)],
            capture_output=True, text=True, check=True
        )
        prediction = json.loads(result.stdout.strip())

        if "error" in prediction:
            return None, prediction["error"], 500

        return {
            "image_path": f"uploads/{unique_filename}",
            "diagnosis": prediction.get("diagnosis", "Unknown"),
            "confidence": prediction.get("confidence", "N/A"),
            "elaboration": prediction.get("elaboration", "No elaboration available.")
        }, None, 200

    except subprocess.CalledProcessError as e:
        return None, f"Prediction failed: {e.stderr.strip()}", 500
    except json.JSONDecodeError:
        return None, f"Invalid output from {script_name}.py", 500
    except Exception as e:
        return None, str(e), 500

# Routes
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
    if "image" not in request.files:
        return render_template("error.html", error="No file uploaded"), 400  # Better error handling

    result, error, status = handle_prediction("BTT", request.files["image"])
    if result:
        return render_template("result.html", 
                               image_path=result["image_path"],
                               diagnosis=result["diagnosis"],
                               confidence=result["confidence"],
                               elaboration=result["elaboration"])
    else:
        return render_template("error.html", error=error), status


@app.route("/predict-pneumonia", methods=["POST"])
def predict_pneumonia():
    if "image" not in request.files:
        return render_template("error.html", error="No file uploaded"), 400

    result, error, status = handle_prediction("PT", request.files["image"])
    if result:
        return render_template("result.html", 
                               image_path=result["image_path"],
                               diagnosis=result["diagnosis"],
                               confidence=result["confidence"],
                               elaboration=result["elaboration"])
    else:
        return render_template("error.html", error=error), status


@app.route("/download_report")
def download_report():
    """Generate PDF report."""
    diagnosis = request.args.get("diagnosis", "No diagnosis provided")
    confidence = request.args.get("confidence", "N/A")
    elaboration = request.args.get("elaboration", "No elaboration available.")
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # PDF styling
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 750, "Medical Diagnosis Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Diagnosis: {diagnosis}")
    c.drawString(100, 700, f"Confidence: {confidence}%")
    c.drawString(100, 680, "Clinical Notes:")
    text = c.beginText(100, 660)
    text.setFont("Helvetica", 10)
    text.textLines(elaboration)
    c.drawText(text)
    
    c.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="diagnosis_report.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)