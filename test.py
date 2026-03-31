import requests
import time

URL = "https://driver-telematics-system.onrender.com/predict"   # 🔥 CHANGE THIS

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
# HARSH ACCELERATION
# =========================
print("🚀 HARSH ACCELERATION")

for _ in range(12):   # 12 sec → overrides window
    send(3.5, 0.0, 9.6, 50)
    time.sleep(1)

# small gap
for _ in range(3):
    send(0.1, 0.0, 9.8, 30)
    time.sleep(1)

# =========================
# HARSH BRAKING
# =========================
print("🛑 HARSH BRAKING")

for _ in range(12):
    send(-4.0, 0.0, 9.8, 10)
    time.sleep(1)

print("✅ TEST COMPLETE")