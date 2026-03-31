import requests, time

url = "https://driver-telematics-system.onrender.com/predict"

data = {
    "ax": 0.1,
    "ay": -2.0,
    "az": 9.6,
    "speed": 35,
    "lat": 13.08,
    "lon": 80.27
}

for i in range(12):
    print(requests.post(url, json=data).json())
    time.sleep(0.5)