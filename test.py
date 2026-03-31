
import requests
import time

URL = "https://driver-telematics-system.onrender.com/predict"   # 🔥 change this

lat = 13.0827
lon = 80.2707

def send(ax, ay, az, speed):
    global lat, lon
    lat += 0.00005
    lon += 0.00005

    data = {
        "ax": ax,
        "ay": ay,
        "az": az,
        "speed": speed,
        "lat": lat,
        "lon": lon
    }

    requests.post(URL, json=data)

print("🚨 HARSH TEST START")

# =========================
# HARD ACCELERATION
# =========================
print("🚀 Strong Acceleration")
for _ in range(8):
    send(3.5, 0.2, 9.5, 50)
    time.sleep(1)

# =========================
# HARD BRAKING
# =========================
print("🛑 Strong Braking")
for _ in range(8):
    send(-4.0, 0.1, 9.8, 15)
    time.sleep(1)

# =========================
# SHARP RIGHT TURN
# =========================
print("↪️ Sharp Right Turn")
for _ in range(8):
    send(0.2, -3.5, 9.6, 30)
    time.sleep(1)

# =========================
# SHARP LEFT TURN
# =========================
print("↩️ Sharp Left Turn")
for _ in range(8):
    send(0.2, 3.5, 9.6, 30)
    time.sleep(1)

print("✅ HARSH TEST DONE")