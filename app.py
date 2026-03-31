
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# =========================
# LOAD MODEL
# =========================
model = joblib.load("driver_model.pkl")

# =========================
# INPUT FORMAT FROM ESP32
# =========================
class SensorData(BaseModel):
    timestamp: str
    meanX: float
    meanY: float
    meanZ: float
    speed: float
    lat: float
    lon: float

# =========================
# STORE LATEST DATA
# =========================
latest_data = {
    "timestamp": "",
    "meanX": 0,
    "meanY": 0,
    "meanZ": 0,
    "speed": 0,
    "lat": 0,
    "lon": 0,
    "behavior": "Waiting..."
}

# =========================
# PREDICTION API
# =========================
@app.post("/predict")
def predict(data: SensorData):

    meanX = data.meanX
    meanY = data.meanY
    meanZ = data.meanZ
    speed = data.speed
    lat = data.lat
    lon = data.lon
    timestamp = data.timestamp

    # MODEL INPUT (ONLY 3 FEATURES)
    X = np.array([[meanX, meanY, meanZ]])

    pred = model.predict(X)[0]

    # Map labels
    label_map = {
        1: "Sudden Acceleration",
        2: "Right Turn",
        3: "Left Turn",
        4: "Sudden Braking"
    }

    behavior = label_map.get(pred, "Unknown")

    # Store latest data
    latest_data.update({
        "timestamp": timestamp,
        "meanX": meanX,
        "meanY": meanY,
        "meanZ": meanZ,
        "speed": speed,
        "lat": lat,
        "lon": lon,
        "behavior": behavior
    })

    return {"driver_behavior": behavior}

# =========================
# LIVE DATA FOR DASHBOARD
# =========================
@app.get("/data")
def get_data():
    return latest_data

# =========================
# DASHBOARD
# =========================
@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html", encoding="utf-8") as f:
        return f.read()

