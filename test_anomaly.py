# test_anomaly.py

from anomaly_detector import detect_anomaly

history = [
    250,
    270,
    260,
    280,
    275
]

print(
    detect_anomaly(
        history,
        900
    )
)