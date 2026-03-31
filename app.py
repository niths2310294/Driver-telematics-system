```python
from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os

app = Flask(__name__)

# =========================
# LOAD MODEL
# =========================
MODEL_PATH = os.path.join("model", "driver_model.pkl")
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
# DASHBOARD
# =========================
@app.route('/')
def home():
    return render_template("index.html", data=latest_data)

# =========================
# ESP32 API
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
            "meanX": round(meanX, 3),
            "meanY": round(meanY, 3),
            "meanZ": round(meanZ, 3),
            "prediction": result
        }

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# HEALTH CHECK
# =========================
@app.route('/health')
def health():
    return "OK", 200

# =========================
# RUN (RENDER FIX)
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
```
