
from flask import Flask, request, jsonify, send_file
import joblib
import numpy as np
import os

app = Flask(__name__)

# =========================
# LOAD MODEL (NO FOLDER)
# =========================
MODEL_PATH = "driver_model.pkl"
model = joblib.load(MODEL_PATH)

# =========================
# STORE LATEST DATA
# =========================
latest_data = {
    "meanX": 0,
    "meanY": 0,
    "meanZ": 0,
    "prediction": "Waiting..."
}

# =========================
# DASHBOARD (HTML FILE)
# =========================
@app.route('/')
def home():
    return send_file("dashboard.html")

# =========================
# API FOR ESP32
# =========================
@app.route('/predict', methods=['POST'])
def predict():
    global latest_data

    try:
        data = request.get_json()

        meanX = float(data['meanX'])
        meanY = float(data['meanY'])
        meanZ = float(data['meanZ'])

        features = np.array([[meanX, meanY, meanZ]])
        pred = model.predict(features)[0]

        label_map = {
            1: "Sudden Acceleration",
            2: "Right Turn",
            3: "Left Turn",
            4: "Sudden Braking"
        }

        result = label_map.get(pred, "Unknown")

        latest_data = {
            "meanX": meanX,
            "meanY": meanY,
            "meanZ": meanZ,
            "prediction": result
        }

        return jsonify({
            "prediction": result,
            "data": latest_data
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# GET LATEST DATA (FOR DASHBOARD)
# =========================
@app.route('/data')
def get_data():
    return jsonify(latest_data)

# =========================
# HEALTH CHECK
# =========================
@app.route('/health')
def health():
    return "OK", 200

# =========================
# RUN (RENDER)
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
