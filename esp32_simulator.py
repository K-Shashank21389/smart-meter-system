import requests
import random

meter_no = "240069381738"

current_reading = random.randint(1700, 1800)

response = requests.post(
    "http://127.0.0.1:8000/meter-reading",
    json={
        "meter_no": meter_no,
        "current_reading": current_reading
    }
)

print(response.json())