import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Load the YOLO model
model = YOLO("yolov8n.pt")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def check_violation(results):
    """ Check if phone and face bounding boxes intersect (violation). """
    phone_boxes = []
    face_boxes = []

    for box in results[0].boxes:
        cls = int(box.cls)
        xyxy = box.xyxy[0].tolist()  # Bounding box coordinates [x1, y1, x2, y2]

        # Check for phone and face classes (adjust class IDs based on your model)
        if cls == 67:  # Phone class ID (adjust based on YOLO version)
            phone_boxes.append(xyxy)
        elif cls == 0:  # Person class ID (assumed to contain face)
            face_boxes.append(xyxy)

    # Check if any phone box overlaps with any face box
    for phone in phone_boxes:
        for face in face_boxes:
            if boxes_overlap(phone, face):
                return "🚨 Violation detected: Phone near face!"

    return "✅ No violation detected."

def boxes_overlap(box1, box2):
    """ Check if two bounding boxes overlap. """
    x1, y1, x2, y2 = box1
    a1, b1, a2, b2 = box2

    # Check if boxes intersect
    return not (x2 < a1 or a2 < x1 or y2 < b1 or b2 < y1)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files:
        return "No file part"

    file = request.files["image"]

    if file.filename == "":
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Run YOLOv8 on the uploaded image
        results = model(filepath)

        # Save the result image
        results[0].save(filename="static/result.jpg")

        # Check for violations
        violation_text = check_violation(results)

        return render_template("index.html", 
                               uploaded_image=filepath, 
                               result_image="static/result.jpg",
                               violation_text=violation_text)

    return "Invalid file type"

if __name__ == "__main__":
    app.run(debug=True)
