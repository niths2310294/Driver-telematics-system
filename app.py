
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import numpy as np
import sqlite3
from datetime import datetime

app = FastAPI()

# =========================
# LOAD MODEL
# =========================
model = joblib.load("driver_model.pkl")

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("driver_logs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    end_time TEXT,
    duration REAL,
    avg_speed REAL
)
""")
conn.commit()

# =========================
# INPUT FORMAT
# =========================
class SensorData(BaseModel):
    ax: float
    ay: float
    az: float
    speed: float
    lat: float
    lon: float

# =========================
# GLOBALS
# =========================
latest_data = {
    "timestamp": "",
    "meanX": 0,
    "meanY": 0,
    "meanZ": 0,
    "speed": 0,
    "lat": 0,
    "lon": 0,
    "behavior": "Normal"
}

trip_active = False
trip_start_time = None
last_moving_time = None
speed_buffer = []

# Sliding window
window_size = 10
acc_buffer = []

# =========================
# PREDICT
# =========================
@app.post("/predict")
def predict(data: SensorData):

    global latest_data, trip_active, trip_start_time, last_moving_time, speed_buffer, acc_buffer

    ax, ay, az = data.ax, data.ay, data.az
    speed, lat, lon = data.speed, float(data.lat), float(data.lon)

    now = datetime.now()

    # =========================
    # WINDOW MEAN
    # =========================
    acc_buffer.append((ax, ay, az))
    if len(acc_buffer) > window_size:
        acc_buffer.pop(0)

    meanX = sum(a[0] for a in acc_buffer) / len(acc_buffer)
    meanY = sum(a[1] for a in acc_buffer) / len(acc_buffer)
    meanZ = sum(a[2] for a in acc_buffer) / len(acc_buffer)

    # =========================
    # MODEL
    # =========================
    X = np.array([[meanX, meanY, meanZ]])
    pred = model.predict(X)[0]

    label_map = {
        1: "Normal",
        2: "Warning",
        3: "Aggressive",
        4: "Aggressive"
    }

    behavior = label_map.get(pred, "Normal")

    # =========================
    # TRIP START
    # =========================
    if speed > 10 and not trip_active:
        trip_active = True
        trip_start_time = now
        last_moving_time = now
        speed_buffer = []
        print("Trip started")

    if trip_active:
        speed_buffer.append(speed)

    # =========================
    # UPDATE MOVING TIME
    # =========================
    if speed > 10:
        last_moving_time = now

    # =========================
    # TRIP END
    # =========================
    if trip_active and last_moving_time:
        idle_time = (now - last_moving_time).total_seconds()

        if idle_time > 600:
            trip_active = False
            end_time = now

            duration = (end_time - trip_start_time).total_seconds() / 60
            avg_speed = sum(speed_buffer) / len(speed_buffer) if speed_buffer else 0

            cursor.execute("""
            INSERT INTO trips (start_time, end_time, duration, avg_speed)
            VALUES (?, ?, ?, ?)
            """, (
                trip_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration,
                avg_speed
            ))
            conn.commit()

            print("Trip saved")

    # =========================
    # UPDATE LIVE DATA
    # =========================
    latest_data.update({
        "timestamp": now.strftime("%H:%M:%S"),
        "meanX": round(meanX, 3),
        "meanY": round(meanY, 3),
        "meanZ": round(meanZ, 3),
        "speed": round(speed, 2),
        "lat": lat,
        "lon": lon,
        "behavior": behavior
    })

    return {"behavior": behavior}

# =========================
# LIVE DATA
# =========================
@app.get("/data")
def get_data():
    return latest_data

# =========================
# LOGS
# =========================
@app.get("/logs")
def get_logs():
    cursor.execute("SELECT * FROM trips ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    return [
        {
            "start": r[1],
            "end": r[2],
            "duration": r[3],
            "avg_speed": r[4]
        }
        for r in rows
    ]

# =========================
# DASHBOARD
# =========================
@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open("dashboard.html", encoding="utf-8") as f:
        return f.read()

