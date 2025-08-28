from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import cvzone
from ultralytics import YOLO
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

MODEL_PATH = "Weights/best.pt"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"YOLO model not found at {MODEL_PATH}")

yolo_model = YOLO(MODEL_PATH)
class_labels = ['With Helmet', 'Without Helmet']

UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "static/processed"
CROPPED_FOLDER = "static/cropped"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_helmet():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    filename = file.filename
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(PROCESSED_FOLDER, filename)
    cropped_path = os.path.join(CROPPED_FOLDER, filename)

    file.save(input_path)
    print(f"✅ Image Received: {input_path}")

    img = cv2.imread(input_path)
    if img is None:
        return jsonify({"error": "Invalid image format"}), 400

    h, w = img.shape[:2]  # Get image dimensions

    print("🔍 Performing Helmet Detection...")
    results = yolo_model(img)
    
    without_helmet_boxes = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
            conf = float(box.conf[0])
            cls = int(box.cls[0])  # Class index

            if conf > 0.3:
                label = class_labels[cls]
                color = (0, 255, 0) if cls == 0 else (0, 0, 255)  # Green for helmet, Red for no helmet
                
                # Draw detection box
                cvzone.cornerRect(img, (x1, y1, x2-x1, y2-y1), colorC=color)  
                cvzone.putTextRect(img, f'{label} {conf:.2f}', (x1, y1 - 10), scale=0.8, thickness=1, colorR=(255, 0, 0))
                print(f"🟢 Detected: {label} | Confidence: {conf:.2f}")

                # If "Without Helmet", save bounding box
                if cls == 1:
                    without_helmet_boxes.append((x1, y1, x2, y2))

    if without_helmet_boxes:
        # Get the leftmost and rightmost X coordinates
        min_x = min(box[0] for box in without_helmet_boxes) - 100  # Extend left further
        max_x = max(box[2] for box in without_helmet_boxes) + 100  # Extend right further

        # Ensure valid crop boundaries
        min_x = max(0, min_x)
        max_x = min(w, max_x)

        # Crop from the **top (0)** to the bottom of the image
        cropped_img = img[0:h, min_x:max_x]
        cv2.imwrite(cropped_path, cropped_img)
        print(f"🚀 Cropped Image (Top to Bottom) Saved: {cropped_path}")

    cv2.imwrite(output_path, img)
    print(f"✅ Processed Image Saved: {output_path}")

    response_data = {"processed_image_url": f"/static/processed/{filename}"}
    
    if without_helmet_boxes:
        response_data["cropped_image_url"] = f"/static/cropped/{filename}"

    return jsonify(response_data), 200

@app.route('/static/processed/<filename>')
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route('/static/cropped/<filename>')
def serve_cropped_image(filename):
    return send_from_directory(CROPPED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
